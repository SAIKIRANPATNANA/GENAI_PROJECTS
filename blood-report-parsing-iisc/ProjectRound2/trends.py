def get_patient_names_from_db_wrt_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("select distinct name from Patients where user_id  = ?", (user_id,)) 
    patient_names = cursor.fetchall()
    conn.close()
    patient_names =  [patient_name[0] for patient_name in patient_names]
    return patient_names

def get_report_ids_n_test_names(patient_name, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("select report_id,json_extract(parsed_report, '$.test_name')from Reports where patient_id in (select patient_id from Patients where user_id = ? and name = ?)", (1,"Mr. Saubhik Bhaumik"))
    reports  = cursor.fetchall()
    return reports

def grouping_test_names(test_names):
  llm = ChatGroq(model_name="mixtral-8x7b-32768", groq_api_key=groq_api_key)
  class TestGroup(BaseModel):
      standardized_test_name: str = Field(..., description="Unique standardized test name.")
      report_ids: list[int] = Field(..., description="List of report IDs associated with this test name.")

  class TestGroupingOutput(BaseModel):
      grouped_tests: list[TestGroup] = Field(..., description="List of grouped test names and their report IDs.")

  def group_test_names_with_llm(test_names):
      structured_llm = llm.with_structured_output(TestGroupingOutput)
      formatted_test_names = "\n".join([f"- {t}" for _, t in test_names])
      prompt_template = f"""
      The following test names were found for a patient:
      {formatted_test_names}

      Your task:
      - Group test names that refer to the same medical test.
      - Return a structured JSON output with standardized test names and their report IDs.

      Expected JSON Output:
      {{
        "grouped_tests": [
          {{
            "standardized_test_name": test name,
            "report_ids": list of report ids
          }},
          {{
            "standardized_test_name": test name,
            "report_ids": list of report ids
          }}
        ]
      }}
      """

      structured_response = structured_llm.invoke(prompt_template)
      
      return structured_response.dict() 
  return group_test_names_with_llm(test_names)
import sqlite3
import json

def get_lab_results_for_test(report_ids):
    """
    Fetches lab results for the given report IDs.
    """
    conn = sqlite3.connect("blood_reports.db")
    cursor = conn.cursor()

    query = f"""
        SELECT report_id, json_extract(parsed_report, '$.lab_results') 
        FROM Reports 
        WHERE report_id IN ({",".join(["?"] * len(report_ids))})
    """

    cursor.execute(query, report_ids)
    results = cursor.fetchall()
    conn.close()
    lab_results = {report_id: json.loads(data) for report_id, data in results if data}
    return lab_results  

def standardizing_param_names_with_llm(lab_results):
  class StandardizedParameter(BaseModel):
      original_name: str = Field(..., description="Original test name.")
      standardized_name: str = Field(..., description="Unified standard test name.")

  class StandardizedLabResults(BaseModel):
      standardized_tests: list[StandardizedParameter] = Field(..., description="List of standardized lab test parameters.")
      
  llm = ChatGroq(model_name="mixtral-8x7b-32768", groq_api_key=groq_api_key)

  def standardize_param_names_with_llm(lab_results):
      structured_llm = llm.with_structured_output(StandardizedLabResults)
      """
      Uses an LLM to standardize test names dynamically.
      """
      test_param_names = list({param for report in lab_results.values() for param in report.keys()})

      prompt_template = f"""
      The following blood test parameter names were extracted:
      {test_param_names}

      Your task:
      - Standardize each parameter name to a commonly accepted medical term.
      - Return a structured JSON mapping the original test name to the standardized name.

      Example Output:
      {{
        "standardized_tests": [
          {{
            "original_name": "Hb",
            "standardized_name": "Hemoglobin"
          }},
          {{
            "original_name": "WBC Count",
            "standardized_name": "White Blood Cell Count"
          }}
        ]
      }}
      """

      structured_response = structured_llm.invoke(prompt_template)
      
      return structured_response.dict()
  return standardize_param_names_with_llm(lab_results)

def apply_standardized_names(lab_results, standardization_map):
    """
    Applies standardized names to lab test results.
    """
    standardized_results = []
    
    for report_id, tests in lab_results.items():
        standardized_report = {"report_id": report_id}
        
        for param, details in tests.items():
            standardized_name = next((item["standardized_name"] for item in standardization_map["standardized_tests"] if item["original_name"] == param), param)
            standardized_report[standardized_name] = details["value"]
        
        standardized_results.append(standardized_report)

    return pd.DataFrame(standardized_results)

def generate_pandas_profiling_report(df, filename="trend_analysis.html"):
    """
    Performs Pandas Profiling and saves the report as an HTML file.
    """
    profile = ProfileReport(df, explorative=True)
    profile.to_file(filename)
    return filename


def get_selected_param_data(report_ids, selected_param):
    """
    Fetches the selected parameter's values along with the uploaded timestamp.
    """
    conn = sqlite3.connect("blood_reports.db")
    cursor = conn.cursor()

    query = f"""
        SELECT uploaded_at, json_extract(report_data, '$.lab_results.{selected_param}.value') AS param_value
        FROM Reports 
        WHERE report_id IN ({",".join(["?"] * len(report_ids))})
    """

    cursor.execute(query, report_ids)
    results = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(results, columns=["uploaded_at", selected_param])
    df["uploaded_at"] = pd.to_datetime(df["uploaded_at"]) 
 
    return df

def plot_scatter(df, selected_param):
    """
    Plots a scatter plot of the selected parameter over time.
    """
    plt.figure(figsize=(10, 5))
    plt.scatter(df["uploaded_at"], df[selected_param], color="blue", alpha=0.7, label=selected_param)
    
    plt.xlabel("Upload Date")
    plt.ylabel(f"{selected_param} Value")
    plt.title(f"Trend of {selected_param} Over Time")
    plt.xticks(rotation=45)
    plt.legend()
    
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("scatter_plot.png")  # Save plot as an image
    plt.show()

def get_uploaded_timestamps(report_ids):
    """
    Fetches the uploaded timestamps for the given report IDs.
    """
    conn = sqlite3.connect("blood_reports.db")
    cursor = conn.cursor()

    query = f"""
        SELECT report_id, uploaded_at
        FROM Reports 
        WHERE report_id IN ({",".join(["?"] * len(report_ids))})
    """

    cursor.execute(query, report_ids)
    results = cursor.fetchall()
    conn.close()

    return pd.DataFrame(results, columns=["report_id", "uploaded_at"])

def merge_uploaded_timestamps(df, report_ids):
    """
    Merges uploaded timestamps with the existing DataFrame of lab results.
    """
    timestamps_df = get_uploaded_timestamps(report_ids)

    # Ensure 'report_id' exists in the main DataFrame
    if "report_id" in df.columns:
        df = df.merge(timestamps_df, on="report_id", how="left")
    
    return df

#Eg Workflow
# user_id = 1
# patients = get_patient_names_from_db_wrt_user(user_id)
# patient = patients[0]
# test_names = get_report_ids_n_test_names(patient,user_id)
# grouped_test_names = grouping_test_names(test_names)
# selected_test_name_report_ids = grouped_test_names['grouped_tests'][0]['report_ids']
# lab_results = get_lab_results_for_test(selected_test_name_report_ids)
# mapping = standardizing_param_names_with_llm(lab_results)
# df = apply_standardized_names(lab_results, mapping)
# generate_pandas_profiling_report(df)
# df_updated = merge_uploaded_timestamps(df, selected_test_name_report_ids)
# plot_scatter(df_updated, df.columns[2])