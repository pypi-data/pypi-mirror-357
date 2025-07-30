import pandas as pd
import numpy as np
import sempy.fabric as sfabric
from thefuzz import fuzz
from .report import FabricAnalyticsReport
import logging 
from concurrent.futures import ThreadPoolExecutor, as_completed
logger = logging.getLogger(__name__)

class BaseValidator:
    def __init__(
            self, 
            report_new: FabricAnalyticsReport, 
            report_old: FabricAnalyticsReport, 
            all_items: pd.DataFrame, 
            run_id: str, 
            stream: str
        ):
        self.report_new = report_new
        self.report_old = report_old
        self.all_items = all_items
        self.run_id = run_id
        self.stream = stream
    
    def _validate_value(self, new_val, old_val, margin_of_error) -> bool:
        if pd.isna(new_val) or pd.isna(old_val):
            return False 
        
        # Case 1: Fuzzy match if both values are strings
        if isinstance(new_val, str) and isinstance(old_val, str):
            # similarity_score = fuzz.ratio(new_val.strip(), old_val.strip())
            # return similarity_score >= 100 - margin_of_error
            return new_val.strip() == old_val.strip()

        # Case 2: Numeric comparison if both values are numbers
        try:
            new_val_float = float(new_val)
            old_val_float = float(old_val)
            lower_bound = old_val_float * (1 - margin_of_error / 100)
            upper_bound = old_val_float * (1 + margin_of_error / 100)
            return lower_bound <= new_val_float <= upper_bound
        except (ValueError, TypeError):
            return False  # Incompatible types for numeric comparison
        
    
class MeasureValidator(BaseValidator):

    def get_measure_values( self, dataset, workspace, measurelist, max_workers=20):
        """
            Evaluates a list of measures in batches using parallel processing.

            Args:
                self: The instance of the class the function belongs to (if any).
                dataset: The dataset to evaluate against.
                workspace: The workspace to use.
                measurelist: A list of measures to evaluate.
                max_workers

            Returns:
                A pandas DataFrame with a single row, where columns are measures and values are their evaluations.
        """
        def evaluate(measure):
            try:
                df_eval = sfabric.evaluate_measure(
                    dataset=dataset,
                    workspace=workspace,
                    measure=measure
                )
                value = df_eval.iloc[0, 0] if not df_eval.empty else None
                return measure, value
            except Exception as e:
                logger.warning(f"Failed to evaluate measure '{measure}': {e}")
                return measure, None

        
        try : 
            return sfabric.evaluate_measure(
                dataset=self.report_new.datasetid,
                workspace=self.report_new.workspaceid,
                measure=measurelist)
        except Exception as e:
            logger.warning('Could not retrive all measures in a go, trying one by one will take time')
            pass

        result = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(evaluate, measure): measure for measure in measurelist}
            for future in as_completed(futures):
                measure, value = future.result()
                result[measure] = value

        return pd.DataFrame([result])

    def validate_measure_values(self, margin_of_error=5.0):

        matched_measures = self.all_items[
            (self.all_items['origin'] == 'both') &
            (self.all_items['data_type_new'].str.strip().str.lower() != 'variant') &
            (self.all_items['data_type_old'].str.strip().str.lower() != 'variant')
        ][[
            'table_name_new',
            'field_name_new',
            'field_name_old',
            'data_type_new',
            'data_type_old',
            'expression_old',
            'expression_new',
            'origin',
            'best_score'
        ]].dropna(subset=['field_name_new', 'field_name_old'])

        if matched_measures.empty:
            return pd.DataFrame()

        try:
            new_eval = self.get_measure_values(
                dataset=self.report_new.datasetid,
                workspace=self.report_new.workspaceid,
                measurelist=list(matched_measures['field_name_new'])
            )
            old_eval = self.get_measure_values(
                dataset=self.report_old.datasetid,
                workspace=self.report_old.workspaceid,
                measurelist=list(matched_measures['field_name_old'])
            )
            new_eval_pivot = new_eval.melt(var_name='field_name_new', value_name='new_report_value')
            old_eval_pivot = old_eval.melt(var_name='field_name_old', value_name='old_report_value')

            merged = pd.merge(matched_measures, new_eval_pivot, on='field_name_new', how='left')
            merged = pd.merge(merged, old_eval_pivot, on='field_name_old', how='left')

            merged['new_val_numeric'] = pd.to_numeric(merged['new_report_value'], errors='coerce')
            merged['old_val_numeric'] = pd.to_numeric(merged['old_report_value'], errors='coerce')
            
            merged['value_difference'] = merged['new_val_numeric'] - merged['old_val_numeric']
            merged['value_difference_percent'] = np.where(
                (merged['old_val_numeric'] == 0) |
                (merged['old_val_numeric'].isna()) |
                (merged['new_val_numeric'].isna()),
                '<NA>',
                (((merged['new_val_numeric'] - merged['old_val_numeric']) * 100) / merged['old_val_numeric'])
                .round(2).astype(str) + '%'
            )
            merged.loc[(merged['value_difference'] == 0) & (merged['value_difference_percent'] == '<NA>'),'value_difference_percent'] = '0.0%'
            merged['is_value_similar'] = merged.apply(
                lambda row: self._validate_value(row['new_report_value'], row['old_report_value'], margin_of_error), axis=1
            )
            merged['is_data_type_same'] = merged['data_type_new'] == merged['data_type_old']
            merged['is_expression_same'] = merged['expression_new'] == merged['expression_old']
            merged['run_id'] = self.run_id
            merged['Stream'] = self.stream

            final_cols = [
                'run_id',
                'Stream',
                'table_name_new',
                'field_name_new',
                'field_name_old',
                'best_score',
                'origin',
                'new_report_value',
                'old_report_value',
                'value_difference', 
                'value_difference_percent',
                'is_value_similar', 
                'is_data_type_same', 
                'is_expression_same'
            ]
            return merged[final_cols]
        except Exception as e:
            print(f"Error in measure validation: {e}")
            return pd.DataFrame()

class TableValidator(BaseValidator):

    def _get_table_row_count(self, report, table_name) -> int:
        query = f'EVALUATE ROW("RowCount", COUNTROWS(\'{table_name}\'))'
        try:
            df = sfabric.evaluate_dax(dataset=report.datasetid, workspace=report.workspaceid, dax_string=query)
            colname = df.columns[0]
            value = df[colname].iloc[0]
            return 0 if pd.isna(value) else int(value)
        except Exception as e:
            logger.error(f"Error fetching row count for table : {e}")
            return -1

    def validate_row_counts(self, margin_of_error=5.0) -> pd.DataFrame:
        results = []
        matched_tables = self.all_items

        for _, row in matched_tables.iterrows():
            table_new = row['table_name_new']
            table_old = row['table_name_old']

            count_new = self._get_table_row_count(self.report_new, table_new)
            count_old = self._get_table_row_count(self.report_old, table_old)
            
            diff = count_new - count_old
            diff_pct = f"{((diff) / count_old * 100):.2f}%" if count_old != 0 else "∞%"

            results.append({
                'run_id': self.run_id,
                'Stream': self.stream,
                'table_name_new': table_new,
                'table_name_old': table_old,
                'best_score': row['best_score'],
                'origin': 'both',
                'row_count_new': count_new,
                'row_count_old': count_old,
                'row_count_difference': diff,
                'row_count_diff_percentage': diff_pct,
                'is_value_similar': self._validate_value(count_new, count_old, margin_of_error),
            })
        
        return pd.DataFrame(results)

class ColumnValidator(BaseValidator):

    def _read_table(self,table_name) -> None:
        self._new_tables_data = {}
        try:
            self._new_tables_data[table_name] = sfabric.read_table(
                dataset=self.report_new.datasetid,
                workspace=self.report_new.workspaceid,
                table=table_name
            )
        except Exception as e:
            logger.warning(f"Error reading new table '{table_name}': {e}")
            self._new_tables_data[table_name] = pd.DataFrame()

    def _generate_distinct_count_dax(self,columns: list[str],table_name) -> str:
        rows = []
        for col in columns:
            row = f'ROW("ColumnName", "{col}", "DistinctCount", COUNTROWS(SUMMARIZE(\'{table_name}\', \'{table_name}\'[{col}])))'
            rows.append(row)
        return  "EVALUATE\nUNION(\n    " + ",\n    ".join(rows) + "\n)"

    def _get_column_distinct_counts(self, table_name: str, columns: list[str], report: FabricAnalyticsReport) -> pd.DataFrame | None:
        """
        Executes a DAX query to fetch distinct counts for the given columns and table.
        """
        if not columns:
            logging.warning(f"No columns provided for table '{table_name}' in dataset {report.datasetid}.")
            return None
            
        dax_query = self._generate_distinct_count_dax(columns=columns, table_name=table_name)
        if dax_query is None:
            return None
            
        try:
            df = sfabric.evaluate_dax(
                dataset=report.datasetid,
                workspace=report.workspaceid,
                dax_string=dax_query
            )
            df.columns = ["ColumnName", "DistinctCount"]
            if(len(df) == 0):
                logging.warning(f"No row count returned for columns in table '{table_name}'")
            return df
        except Exception as e:
            logging.error(f"Error fetching distinct row count for columns in table '{table_name}': {e}")
            return None
    
    def __get_distinct_values_dax(self, report: FabricAnalyticsReport, table: str, column: str) -> set:
        try:
            dax = f"EVALUATE SELECTCOLUMNS(DISTINCT('{table}'[{column}]), \"Value\", '{table}'[{column}])"
            df = sfabric.evaluate_dax(dataset=report.datasetid, workspace=report.workspaceid, dax_string=dax)
            return set(df["[Value]"].dropna().unique()) if "[Value]" in df.columns else set()
        except Exception as e:
            logger.warning(f"DAX DISTINCT values failed for {table}.{column}: {e}")
            return set()

    def validate_distinct_counts(self, margin_of_error: float = 5.0) -> pd.DataFrame:
        """
        Validates the distinct count of values for all common columns across all common tables.

        Args:
            margin_of_error (float): The allowed percentage difference between old and new counts.

        Returns:
            pd.DataFrame: A dataframe containing the validation results for each column,
                          including new/old counts and whether the validation passed.
        """
        validation_results = []
        
        # Find common tables based on the mapping in all_items
        common_tables = self.all_items[['table_name_new', 'table_name_old']].drop_duplicates()

        for _, row in common_tables.iterrows():
            table_name_new = row['table_name_new']
            table_name_old = row['table_name_old']

            logging.info(f"Validating distinct counts for table: '{table_name_new}' (new) vs '{table_name_old}' (old)")

            # Filter columns for the current table pair
            table_columns_map = self.all_items[
                (self.all_items['table_name_new'] == table_name_new) &
                (self.all_items['table_name_old'] == table_name_old)
            ]

            cols_new = table_columns_map['field_name_new'].unique().tolist()
            cols_old = table_columns_map['field_name_old'].unique().tolist()

            # Fetch distinct counts for both new and old reports
            df_new = self._get_column_distinct_counts(table_name_new, cols_new, self.report_new)
            df_old = self._get_column_distinct_counts(table_name_old, cols_old, self.report_old)

            if df_new is None or df_old is None:
                logging.warning(f"Could not retrieve data for one or both tables: {table_name_new}, {table_name_old}. Skipping.")
                continue

            # Rename columns for merging
            df_new = df_new.rename(columns={"ColumnName": "field_name_new", "DistinctCount": "distinct_count_new"})
            df_old = df_old.rename(columns={"ColumnName": "field_name_old", "DistinctCount": "distinct_count_old"})
            
            # Merge results based on the column mapping
            merged_df = pd.merge(table_columns_map, df_new, on="field_name_new")
            merged_df = pd.merge(merged_df, df_old, on="field_name_old")

            # Perform validation for each column
            merged_df['is_value_similar'] = merged_df.apply(
                lambda r: self._validate_value(r['distinct_count_new'], r['distinct_count_old'], margin_of_error),
                axis=1
            )
            merged_df['value_difference'] = merged_df['distinct_count_new'] - merged_df['distinct_count_old']
            merged_df['value_difference_percent'] = np.where(
                (merged_df['distinct_count_new'] == 0) |
                (merged_df['distinct_count_new'].isna()) |
                (merged_df['distinct_count_old'].isna()),
                '<NA>',
                (((merged_df['distinct_count_old'] - merged_df['distinct_count_new']) * 100) / merged_df['distinct_count_new'])
                .round(2).astype(str) + '%'
            )
            merged_df.loc[(merged_df['value_difference'] == 0) & (merged_df['value_difference_percent'] == '<NA>'),'value_difference_percent'] = '0.0%'

            merged_df['is_data_type_same'] = merged_df['data_type_new'] == merged_df['data_type_old']
            enriched_rows = []

            for _, r in merged_df.iterrows():
                column_new = r['field_name_new']
                column_old = r['field_name_old']
                enriched = r.to_dict()
                try:
                    if(r['distinct_count_new'] > 50 or r['distinct_count_old'] > 50):
                        enriched.update({
                            "new_values": None,
                            "missing_values": None,
                            "new_values_count": None,
                            "missing_value_count": None,
                            "distinct_value_diff": None,
                            "value_missing_present": None
                        })
                        enriched_rows.append(enriched)
                        continue

                    enriched_rows.append(enriched)
                    values_new = self.__get_distinct_values_dax(self.report_new, table_name_new, column_new)
                    values_old = self.__get_distinct_values_dax(self.report_old, table_name_old, column_old)
                    new_values = sorted(values_new - values_old)
                    missing_values = sorted(values_old - values_new)
                    new_values_count = len(new_values)
                    missing_value_count = len(missing_values)
                    distinct_value_diff = len(new_values) + len(missing_values)
                    value_missing_present = ', '.join([f"+{v}" for v in new_values] + [f"-{v}" for v in missing_values])
                    enriched.update({
                        "new_values": ', '.join(new_values),
                        "missing_values": ', '.join(missing_values),
                        "new_values_count": f"+{new_values_count}",
                        "missing_value_count": f"-{missing_value_count}",
                        "distinct_value_diff": distinct_value_diff,
                        "value_missing_present": value_missing_present
                    })
                    enriched_rows.append(enriched)
                except Exception as e:
                    logger.error(f"Error comparing values for {table_name_new}.{column_new}: {e}")
                    enriched.update({
                        "new_values": None,
                        "missing_values": None,
                        "new_values_count": None,
                        "missing_value_count": None,
                        "distinct_value_diff": None,
                        "value_missing_present": None
                    })
                    enriched_rows.append(enriched)
                    continue
            if enriched_rows:
                validation_results.append(pd.DataFrame(enriched_rows))
    
        if not validation_results:
            return pd.DataFrame() 

        return pd.concat(validation_results, ignore_index=True)
    
