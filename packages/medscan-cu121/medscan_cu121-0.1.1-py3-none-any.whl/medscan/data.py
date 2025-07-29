from __future__ import annotations

import math
from typing import Optional, Sequence, Tuple

import pandas as pd
from sklearn.model_selection import train_test_split


class Data:
    """
    Utility class: `split() -> train_df, val_df, test_df = Data.split(df, target_cols=["label"])`
    """

    # ------------------------------------------------------------------
    #  SPLIT
    # ------------------------------------------------------------------
    @staticmethod
    def split(
        data: pd.DataFrame,
        *,
        train_frac: float = 0.7,
        val_frac: float = 0.15,
        seed: int = 42,
        shuffle: bool = True,
        stratify: bool = True,
        target_cols: Optional[Sequence[str]] = None,
        require_all_classes: bool = True,
        shuffle_column: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Parameters
        ----------
        data : DataFrame
        train_frac / val_frac : sum ≤ 1; remainder becomes the test set (or error if >1)
        shuffle           : True  -> shuffle the data (or—when shuffle_column is provided—the groups)
        stratify          : True  -> stratify on target_cols[0]. If shuffle_column is also set,
                            the function will attempt up to 100 group‐level splits and choose the one
                            whose class distribution deviates least from the overall distribution.
        shuffle_column    : column name to shuffle by group. If provided, unique values of this column
                            are first used to partition rows into train/val/test so that all rows sharing
                            the same shuffle_column value land in the same subset.
        require_all_classes : True -> ensure each class is present in every subset (only if stratify=True
                            and shuffle_column is None)
        Returns: train_df, val_df, test_df
        """

        # 1) Validate fraction values
        if not (0 < train_frac < 1) or not (0 <= val_frac < 1):
            raise ValueError("train_frac and val_frac must be in the range (0, 1).")

        total = train_frac + val_frac
        if total > 1.0 and not math.isclose(total, 1.0):
            raise ValueError("train_frac + val_frac must not exceed 1.")

        test_frac = 1.0 - total
        if math.isclose(test_frac, 0.0):
            print("Warning: train_frac + val_frac = 1.0 → no test set will be created.")

        # 2) If shuffle_column is provided and stratify=True, we'll attempt to approximate stratification
        if shuffle_column is not None and stratify:
            if not target_cols:
                raise ValueError("stratify=True but target_cols is not provided.")
            if not shuffle:
                raise ValueError("Stratified splitting requires shuffle=True. Please set shuffle=True when using stratify.")
            # We will override the simpler group-split logic and do 100 trials below
            do_stratified_group_split = True
        else:
            do_stratified_group_split = False

        # 3) If shuffle_column is provided but stratify=False, just do group-level split once
        if shuffle_column is not None and not do_stratified_group_split:
            if shuffle_column not in data.columns:
                raise ValueError(f"shuffle_column '{shuffle_column}' is not present in the DataFrame.")
            # Single‐trial group split (no stratification attempt)
            unique_vals = data[shuffle_column].dropna().unique()
            n_groups = len(unique_vals)

            # Shuffle the group values once
            rnd = pd.Series(unique_vals).sample(frac=1.0, random_state=seed).tolist()

            n_train_groups = int(train_frac * n_groups)
            n_val_groups = int(val_frac * n_groups)
            n_test_groups = n_groups - n_train_groups - n_val_groups

            train_groups = set(rnd[:n_train_groups])
            val_groups = set(rnd[n_train_groups : n_train_groups + n_val_groups])
            test_groups = set(rnd[n_train_groups + n_val_groups :])

            train_df = data[data[shuffle_column].isin(train_groups)].copy()
            val_df = data[data[shuffle_column].isin(val_groups)].copy()
            test_df = (
                data[data[shuffle_column].isin(test_groups)].copy()
                if n_test_groups > 0
                else pd.DataFrame(columns=data.columns)
            )

            if n_test_groups == 0:
                print("Warning: train_frac + val_frac = 1.0 → test set is empty (no groups left).")

        # 4) If we need to attempt stratified group-split
        elif do_stratified_group_split:
            if shuffle_column not in data.columns:
                raise ValueError(f"shuffle_column '{shuffle_column}' is not present in the DataFrame.")

            # Overall class proportions (for target_cols[0])
            target = target_cols[0]
            overall_counts = data[target].dropna().value_counts(normalize=True)
            overall_props = overall_counts.to_dict()

            unique_vals = data[shuffle_column].dropna().unique()
            n_groups = len(unique_vals)
            n_train_groups = int(train_frac * n_groups)
            n_val_groups = int(val_frac * n_groups)
            n_test_groups = n_groups - n_train_groups - n_val_groups

            best_dev = float("inf")
            best_split = None

            for trial in range(100):
                rnd = pd.Series(unique_vals).sample(frac=1.0, random_state=seed + trial).tolist()

                train_groups = set(rnd[:n_train_groups])
                val_groups = set(rnd[n_train_groups : n_train_groups + n_val_groups])
                test_groups = set(rnd[n_train_groups + n_val_groups :])

                df_train = data[data[shuffle_column].isin(train_groups)]
                df_val = data[data[shuffle_column].isin(val_groups)]
                df_test = (
                    data[data[shuffle_column].isin(test_groups)]
                    if n_test_groups > 0
                    else pd.DataFrame(columns=data.columns)
                )

                # Compute deviation: weighted sum of L1 differences
                total_deviation = 0.0
                for subset_df in (df_train, df_val, df_test):
                    if subset_df.empty:
                        # If test fraction is zero, we allow empty test
                        if subset_df is df_test and n_test_groups == 0:
                            continue
                        else:
                            # If any other subset is empty, skip this trial
                            total_deviation = float("inf")
                            break

                    subset_counts = subset_df[target].dropna().value_counts(normalize=True).to_dict()
                    # Ensure every class appears in subset_counts with zero if missing
                    for cls, overall_p in overall_props.items():
                        p_sub = subset_counts.get(cls, 0.0)
                        total_deviation += abs(p_sub - overall_p) * (len(subset_df) / len(data))

                if total_deviation < best_dev:
                    best_dev = total_deviation
                    best_split = (df_train.copy(), df_val.copy(), df_test.copy())
                    if best_dev == 0.0:
                        break  # can't get better than perfect match

            if best_split is None:
                raise RuntimeError("Failed to find any valid stratified group split in 100 trials.")

            train_df, val_df, test_df = best_split
            print(
                f"Warning: Could not strictly stratify due to shuffle_column. "
                f"Chose best split out of 100 random trials with total class‐distribution deviation = {best_dev:.4f}."
            )

        # 5) Normal train_test_split logic when shuffle_column is not provided
        else:
            if stratify and not target_cols:
                raise ValueError("stratify=True but target_cols is not provided.")
            if stratify and not shuffle:
                raise ValueError(
                    "Stratified splitting requires shuffle=True. Please set shuffle=True when using stratify."
                )

            strat_base = data[target_cols[0]] if (stratify and target_cols) else None

            train_df, temp_df = train_test_split(
                data,
                train_size=train_frac,
                random_state=seed,
                shuffle=shuffle,
                stratify=strat_base,
            )

            if math.isclose(test_frac, 0.0):
                val_df = temp_df.copy()
                test_df = pd.DataFrame(columns=data.columns)
                print("Warning: train_frac + val_frac = 1.0 → skipping test set.")
            else:
                val_size = val_frac / (val_frac + test_frac)
                strat_temp = temp_df[target_cols[0]] if (stratify and target_cols) else None
                val_df, test_df = train_test_split(
                    temp_df,
                    train_size=val_size,
                    random_state=seed,
                    shuffle=shuffle,
                    stratify=strat_temp,
                )

        # 6) (Optional) Verify that all classes appear in train/val/test when stratify=True and not using shuffle_column
        if require_all_classes and stratify and shuffle_column is None:
            all_cls = set(data[target_cols[0]].dropna().unique())
            missing: list[str] = []
            for name, part in zip(
                ("train", "val", "test"),
                (
                    train_df,
                    val_df,
                    test_df if (not test_df.empty) else pd.DataFrame(),
                ),
            ):
                if part.empty or target_cols[0] not in part.columns:
                    have = set()
                else:
                    have = set(part[target_cols[0]].dropna().unique())
                if all_cls - have:
                    missing.append(name)

            if missing:
                for m in missing:
                    if m == "test":
                        print(
                            "Warning: Not all classes present in test set. Skipping check for 'test'."
                        )
                    else:
                        raise RuntimeError(
                            f"Missing classes in subset '{m}'. Cannot proceed with stratified splitting."
                        )

        # 7) Print summary and reset index of subsets
        print("\nAfter Data.split():")
        print("  Train:", len(train_df), "rows")
        print("  Val:  ", len(val_df), "rows")
        if test_df is None or test_df.empty:
            print("  Test:  <empty or skipped>")
        else:
            print("  Test: ", len(test_df), "rows")

        return (
            train_df.reset_index(drop=True),
            val_df.reset_index(drop=True),
            test_df.reset_index(drop=True) if (test_df is not None) else None,
        )
