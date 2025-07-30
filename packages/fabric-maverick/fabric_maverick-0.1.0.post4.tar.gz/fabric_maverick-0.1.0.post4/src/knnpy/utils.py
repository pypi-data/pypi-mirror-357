import pandas as pd
from IPython.display import HTML, display

def get_run_details(comparison_obj):
    """
    Generates a summary DataFrame about the comparison run.
    """
    try:
        data = {
            "run_id": [comparison_obj.run_id],
            "Stream": [comparison_obj.stream],
            "new_report_workspace": [f"{comparison_obj.report_new.report_name}_workspace_{comparison_obj.report_new.workspace_name}"],
            "old_report_workspace": [f"{comparison_obj.report_old.report_name}_workspace_{comparison_obj.report_old.workspace_name}"],
            "new_report_refresh_date": [str(comparison_obj.report_new.last_modified_date)],
            "old_report_refresh_date": [str(comparison_obj.report_old.last_modified_date)]
        }
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error generating run details: {e}")
        return pd.DataFrame()

def get_raw_table_details(comparison_obj):
    """
    Returns all table comparison details with a run ID.
    """
    try:
        df = comparison_obj._all_tables.copy()
        df["run_id"] = comparison_obj.run_id
        return df
    except Exception as e:
        print(f"Error retrieving raw table details: {e}")
        return pd.DataFrame()

def get_raw_measure_details(comparison_obj):
    """
    Returns all measure comparison details with a run ID.
    """
    try:
        df = comparison_obj._all_measures.copy()
        df["run_id"] = comparison_obj.run_id
        return df
    except Exception as e:
        print(f"Error retrieving raw measure details: {e}")
        return pd.DataFrame()

def render_dataframe_tabs(df_list):
    """
    Render multiple DataFrames as scrollable tabs in Fabric notebook.
    Adds green/red dot icons in 'is_value_similar' column.

    Parameters:
    - df_list: List of (title, DataFrame) tuples

    Returns:
    - HTML display or raw string
    """
    style = """
    <style>
        .tab { overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }
        .tab button { background-color: inherit; float: left; border: none; outline: none;
                      cursor: pointer; padding: 10px 14px; transition: 0.3s; }
        .tab button:hover { background-color: #ddd; }
        .tab button.active { background-color: #ccc; }
        .tabcontent { display: none; border: 1px solid #ccc; border-top: none;
                      padding: 10px; overflow: auto; max-height: 500px; }
        .tabcontent.active { display: block; }
        table { border-collapse: collapse; width: 100%; }
        th, td { text-align: center; padding: 8px; border: 1px solid #ddd; }
    </style>
    """

    script = """
    <script>
    function openTab(evt, tabName) {
        var i, tabcontent, tablinks;
        tabcontent = document.getElementsByClassName("tabcontent");
        for (i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }
        tablinks = document.getElementsByClassName("tablinks");
        for (i = 0; i < tablinks.length; i++) {
            tablinks[i].className = tablinks[i].className.replace(" active", "");
        }
        document.getElementById(tabName).style.display = "block";
        evt.currentTarget.className += " active";
    }
    </script>
    """

    tab_buttons = '<div class="tab">'
    tab_contents = ''

    for i, (title, df) in enumerate(df_list):
        tab_id = f"tab{i}"
        active_class = "active" if i == 0 else ""

        # Replace True/False in 'is_value_similar' with green/red icons
        if 'is_value_similar' in df.columns:
            df = df.copy()  # Avoid modifying original
            df['Pass_Fail'] = df['is_value_similar'].apply(lambda x: '🟢' if x else '🔴')

        tab_buttons += f'<button class="tablinks {active_class}" onclick="openTab(event, \'{tab_id}\')">{title}</button>'
        df_html = df.to_html(escape=False, index=False)
        tab_contents += f'<div id="{tab_id}" class="tabcontent {active_class}">{df_html}</div>'

    tab_buttons += '</div>'
    html = style + tab_buttons + tab_contents + script
    return display(HTML(html))