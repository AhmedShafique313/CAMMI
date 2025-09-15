from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

# Default global inputs
DEFAULT_INPUTS = {
    "average_deal_size": 15000,
    "target_revenue": 500000,
    "starting_volume": 20000,
    "stages": [
        {"name": "Website Visitors + Database", "conversion": 0.02},
        {"name": "Leads", "conversion": 0.35},
        {"name": "Marketing Qualified Lead (MQL)", "conversion": 0.45},
        {"name": "Sales Qualified Lead (SQL)", "conversion": 0.60},
        {"name": "Opportunity", "conversion": 0.70},
        {"name": "Proposal", "conversion": 0.25},
        {"name": "Customer", "conversion": 1.0},  # Final stage
    ],
}


def forward_calc(inputs):
    """Forward calculation: starting at top-of-funnel, apply conversions downwards"""
    stages = inputs["stages"]
    volumes = []
    current_volume = inputs["starting_volume"]

    for stage in stages:
        volumes.append({"Stage": stage["name"], "Volume": round(current_volume)})
        if stage["conversion"] < 1:
            current_volume = current_volume * stage["conversion"]

    customers = volumes[-1]["Volume"]
    revenue = customers * inputs["average_deal_size"]

    return pd.DataFrame(volumes), customers, revenue


def reverse_calc(inputs):
    """Reverse calculation: starting from target revenue, calculate required funnel volumes"""
    stages = inputs["stages"]
    customers_needed = int(inputs["target_revenue"] / inputs["average_deal_size"])
    required = [{"Stage": "Customer", "Required Volume": customers_needed}]

    current = customers_needed
    for stage in reversed(stages[:-1]):
        current = round(current / stage["conversion"])
        required.insert(0, {"Stage": stage["name"], "Required Volume": current})

    return pd.DataFrame(required)


@app.route("/", methods=["GET", "POST"])
def index():
    inputs = DEFAULT_INPUTS.copy()

    if request.method == "POST":
        inputs["average_deal_size"] = float(request.form["average_deal_size"])
        inputs["target_revenue"] = float(request.form["target_revenue"])
        inputs["starting_volume"] = int(request.form["starting_volume"])

    # Run calcs
    forward_df, customers, revenue = forward_calc(inputs)
    reverse_df = reverse_calc(inputs)

    # Make charts
    fig_forward = px.bar(forward_df, x="Stage", y="Volume", title="Forward Funnel")
    fig_reverse = px.bar(reverse_df, x="Stage", y="Required Volume", title="Reverse Funnel")
    chart_forward = pio.to_html(fig_forward, full_html=False)
    chart_reverse = pio.to_html(fig_reverse, full_html=False)

    return render_template(
        "index.html",
        inputs=inputs,
        forward_table=forward_df.to_html(classes="table table-striped", index=False),
        reverse_table=reverse_df.to_html(classes="table table-striped", index=False),
        customers=customers,
        revenue=revenue,
        chart_forward=chart_forward,
        chart_reverse=chart_reverse,
    )


if __name__ == "__main__":
    app.run(debug=True)
