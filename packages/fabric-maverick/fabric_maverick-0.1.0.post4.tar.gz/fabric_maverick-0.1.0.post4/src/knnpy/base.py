import time
import pandas as pd
from .comparers import TableComparer, MeasureComparer, ColumnComparer
from .validators import TableValidator, MeasureValidator, ColumnValidator
from .utils import get_run_details, get_raw_table_details, get_raw_measure_details, render_dataframe_tabs
from .report import FabricAnalyticsReport 
from sempy import fabric as sfabric
from .token_provider import UserCredAuth

import logging 
import threading
logger = logging.getLogger(__name__)

class ReportComparison:
    """
    Orchestrates the comparison and validation of two FabricAnalyticsReport objects.
    """

    def __init__(
            self, 
            report_new : FabricAnalyticsReport, 
            report_old : FabricAnalyticsReport, 
            stream: str, 
            threshold_score: float = 80.0
            ):
        """
        Initializes the ReportComparison object.

        Args:
            report_new (FabricAnalyticsReport): The new version of the report.
            report_old (FabricAnalyticsReport): The old version of the report.
            stream (str): A label for the comparison stream.
            threshold_score (float, optional): The fuzzy matching threshold. Defaults to 90.0.
        """
        self.report_new = report_new
        self.report_old = report_old
        self.stream = str.lower(str.strip(stream))
        self.threshold_score = threshold_score
        self.run_id = str(int(time.time()))

        # Comparers
        self._table_comparer = TableComparer(self.report_new.tables, self.report_old.tables, self.threshold_score)
        self._all_tables = self._table_comparer.compare()
        self.common_tables = self._all_tables[self._all_tables['origin'] == 'both']
        
        self._column_comparer = ColumnComparer(self.report_new.columns, self.report_old.columns, self.common_tables, self.threshold_score)
        self._all_columns = self._column_comparer.compare()
        self.common_columns = self._all_columns[self._all_columns['origin'] == 'both']
        
        self._measure_comparer = MeasureComparer(self.report_new.measures, self.report_old.measures, self.threshold_score)
        self._all_measures = self._measure_comparer.compare()
        self.common_measures = self._all_measures[self._all_measures['origin'] == 'both']
        
        # Results initialized to None
        self.TableValidationResults = None
        self.MeasureValidationResults = None
        self.ColumnValidationResults = None
        self.RunDetails = get_run_details(self)
        self.RawTables = None
        self.RawMeasures = None

    def run_table_validation(self, margin_of_error: float = 5.0):
        """
        Runs table row count validation.
        
        Args:
            margin_of_error (float, optional): Allowed percentage difference. Defaults to 5.0.
        """
        try:
            logger.info("Starting table validation...")
            start_time = time.time()
            self.table_validator = TableValidator(self.report_new, self.report_old, self.common_tables, self.run_id, self.stream)
            self.TableValidationResults = self.table_validator.validate_row_counts(margin_of_error)
            self.RawTables = get_raw_table_details(self)
            end_time = time.time()
            logger.info(f"Table validation completed in {end_time - start_time:.2f} seconds")
        except Exception as e:
            logger.error(f"Error in table row count validation: {str(e)}")
            self.TableValidationResults = self.RawTables = pd.DataFrame()
    
    def run_column_validation(self, margin_of_error: float = 5.0):
        """
        Runs column level validations.
        
        Args:
            margin_of_error (float, optional): Allowed percentage difference. Defaults to 5.0.
        """
        try:
            logger.info("Starting column validation...")
            start_time = time.time()
            self.column_validator = ColumnValidator(self.report_new, self.report_old, self.common_columns, self.run_id, self.stream)
            self.ColumnValidationResults = self.column_validator.validate_distinct_counts(margin_of_error)
            end_time = time.time()
            logger.info(f"Column validation completed in {end_time - start_time:.2f} seconds")
        except Exception as e:
            logger.error(f"Error in column validation: {str(e)}")
            self.ColumnValidationResults = pd.DataFrame()

    def run_measure_validation(self, margin_of_error: float = 5.0):
        """
        Runs measure level validation.
        
        Args:
            margin_of_error (float, optional): Allowed percentage difference. Defaults to 5.0.
        """
        try:
            logger.info("Starting measure validation...")
            start_time = time.time()
            self.measure_validator = MeasureValidator(self.report_new, self.report_old, self.common_measures, self.run_id, self.stream)
            self.MeasureValidationResults = self.measure_validator.validate_measure_values(margin_of_error)
            self.RawMeasures = get_raw_measure_details(self)
            end_time = time.time()
            logger.info(f"Measure validation completed in {end_time - start_time:.2f} seconds")
        except Exception as e:
            logger.error(f"Error in measure validation: {str(e)}")
            self.MeasureValidationResults = self.RawMeasures = pd.DataFrame()

    def run_all_validations(self, margin_of_error: float = 5.0):
        """
        Runs all validation functions (table, column, measure).
        
        Args:
            margin_of_error (float, optional): Allowed percentage difference. Defaults to 5.0.
        """
        logger.info("Starting all validations ...")
        start_time_parallel = time.time()
        threads = []

        # Creating a thread for each validation function
        table_thread = threading.Thread(target=self.run_table_validation, args=(margin_of_error,))
        column_thread = threading.Thread(target=self.run_column_validation, args=(margin_of_error,))
        measure_thread = threading.Thread(target=self.run_measure_validation, args=(margin_of_error,))

        # Adding threads to a list
        threads.append(table_thread)
        threads.append(column_thread)
        threads.append(measure_thread)

        # Starting all threads
        for thread in threads:
            thread.start()

        # Waiting for all threads to complete
        for thread in threads:
            thread.join()
        end_time_parallel = time.time()
        # results = {
        #     "Measure Validation results" : self.MeasureValidationResults,
        #     "Table Validation results": self.TableValidationResults,
        #     "Column Validation results": self.ColumnValidationResults
        # }
        results = [
            ("Measure Validation results",self.MeasureValidationResults),
            ("Table Validation results", self.TableValidationResults),
            ("Column Validation results", self.ColumnValidationResults)
        ]
        logger.info(f"All validations completed in {end_time_parallel - start_time_parallel:.2f} seconds")

        return render_dataframe_tabs(results)

def ReportCompare(
        OldReport: str, 
        OldReportWorkspace: str, 
        NewReport: str, 
        NewReportWorkspace: str,
        Stream : str|None = None, 
        ExplicitToken: str|None = None,
        Threshold: float = 80,
    ) -> ReportComparison:
    """
    Compare two reports across workspaces.

    Args:
       'old_report' (str): Name of the old report.
       'old_report_workspace' (str): Workspace Name of the old report.
       'new_report' (str): Name of the new report.
       'new_report_workspace' (str): Workspace Name of the new report.
        Stream (str): A label or stream name used for tagging the comparison run.
        ExplicitToken (optional): A token to use for authentication. If None, a default token provider is used.
        Threshold (optional): A fuzzy matching threshold that determines when name comparisons between entities are considered a match.
    Returns:
        ReportComparison Object: This can be futher used to run data validations.
    """    
    if ExplicitToken:
        sfabric._token_provider._get_token = UserCredAuth(ExplicitToken) # type: ignore
    
    Stream = Stream or f"{OldReport}@{OldReportWorkspace}__{NewReport}@{NewReportWorkspace}"
    old_report = FabricAnalyticsReport(OldReport,OldReportWorkspace)
    new_report = FabricAnalyticsReport(NewReport,NewReportWorkspace)

    Compare = ReportComparison(report_new = new_report, report_old= old_report, stream=Stream,threshold_score=Threshold)
    return Compare