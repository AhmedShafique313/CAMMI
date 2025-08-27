from flask import Flask, request, jsonify
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest

app = Flask(__name__)

# Your GA4 property ID
PROPERTY_ID = "502814946" # fake id

@app.route("/analytics")
def analytics():
    client = BetaAnalyticsDataClient()
    
    # Example: get last 7 days of page views
    request_obj = RunReportRequest(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[{"name": "pagePath"}],   # which page
        metrics=[{"name": "screenPageViews"}],  # how many views
        date_ranges=[{"start_date": "7daysAgo", "end_date": "today"}]
    )
    
    response = client.run_report(request_obj)
    
    results = []
    for row in response.rows:
        results.append({
            "page": row.dimension_values[0].value,
            "views": row.metric_values[0].value
        })
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
