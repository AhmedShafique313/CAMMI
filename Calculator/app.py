# all required imports
from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

app = Flask(__name__)

# default stages for this funnel
DEFAULT_STAGES = [
    {"name": "Website Visitors + Database", "conversion": None},
    {"name": "Leads", "conversion": 0.02},
    {"name": "Marketing Qualified Lead (MQL)", "conversion": 0.35},
    {"name": "Sales Qualified Lead (SQL)", "conversion": 0.45},
    {"name": "Opportunity", "conversion": 0.80},
    {"name": "Proposal", "conversion": 0.70},
    {"name": "Customer", "conversion": 0.25},
]


def parse_conversion(raw):
    if raw is None or str(raw).strip() == "":
        return None
    s = str(raw).strip()
    try:
        if "%" in s:
            return float(s.replace("%", "").strip()) / 100.0
        v = float(s)
        return v / 100.0 if v > 1 else v
    except:
        return None

# forward calculation
def forward_calc(stages, starting_volume, average_deal_size):
    n = len(stages)
    vols_float = [float(starting_volume)]

    for i in range(1, n):
        conv = stages[i].get("conversion")
        next_v = vols_float[i - 1] * conv if conv else 0.0
        vols_float.append(next_v)

    rows = []
    for i, stage in enumerate(stages):
        if i < n - 1:
            conv_next = stages[i + 1].get("conversion")
            conv_display = (f"{conv_next * 100:.1f}%" if conv_next is not None else "–")
        else:
            conv_display = "–"

        rows.append({
            "Stage Name": stage["name"],
            "Stage Volume": int(round(vols_float[i])),
            "Conversion to Next": conv_display,
            "Notes": ""
        })

    df_forward = pd.DataFrame(rows)

    customers_float = vols_float[-1]
    customers_display = int(round(customers_float))
    revenue_estimate = customers_float * average_deal_size

    return df_forward, customers_display, revenue_estimate, customers_float

# reverse calculation

def reverse_calc(stages, target_revenue, average_deal_size):
    n = len(stages)
    customers_needed = float(target_revenue) / float(average_deal_size) if average_deal_size else 0.0

    required_float = [None] * n
    required_float[-1] = customers_needed

    for i in range(n - 1, 0, -1):
        conv = stages[i].get("conversion")
        required_float[i - 1] = required_float[i] / conv if conv else 0.0

    top_required = required_float[0] if required_float[0] else 0.0
    rows = []
    for i, stage in enumerate(stages):
        req_disp = int(round(required_float[i])) if required_float[i] is not None else 0
        cum_pct = (required_float[i] / top_required * 100.0) if top_required else 0.0
        rows.append({
            "Stage Name": stage["name"],
            "Required Volume": req_disp,
            "Cumulative Required Conversion": f"{cum_pct:.1f}%"
        })

    df_reverse = pd.DataFrame(rows)
    return df_reverse, customers_needed

# default values but further editable

@app.route("/", methods=["GET", "POST"])
def index():
    average_deal_size = 15000.0
    target_revenue = 500000.0
    starting_volume = 20000
    stages = [dict(s) for s in DEFAULT_STAGES]

    if request.method == "POST":
        average_deal_size = float(request.form.get("average_deal_size", average_deal_size))
        target_revenue = float(request.form.get("target_revenue", target_revenue))

        # 🔹 Modified: fetch all stage names & conversions (no indexed names required)
        names = request.form.getlist("stage_name")
        conversions = request.form.getlist("stage_conversion")

        stages = []
        for i, name in enumerate(names):
            if not name.strip():
                continue
            if i == 0:
                starting_volume = int(request.form.get("starting_volume", starting_volume))
                conv = None
            else:
                conv = parse_conversion(conversions[i]) if i < len(conversions) else None
            stages.append({"name": name.strip(), "conversion": conv})

        if not stages:
            stages = [dict(s) for s in DEFAULT_STAGES]

    forward_df, customers_display, revenue_estimate, customers_float = forward_calc(
        stages, starting_volume, average_deal_size
    )
    reverse_df, customers_needed = reverse_calc(stages, target_revenue, average_deal_size)

# charts and graphs
    try:
        fig_forward = px.bar(forward_df, x="Stage Name", y="Stage Volume", title="Forward Funnel (Bar)")
        fig_reverse = px.bar(reverse_df, x="Stage Name", y="Required Volume", title="Reverse Funnel (Bar)")

        fig_funnel = go.Figure(go.Funnel(
            y=forward_df["Stage Name"], x=forward_df["Stage Volume"], textinfo="value+percent initial"
        ))
        fig_funnel.update_layout(title="Forward Funnel (Funnel Shape)")

        fig_line = px.line(forward_df, x="Stage Name", y="Stage Volume", title="Conversion Drop-off", markers=True)

        losses = forward_df["Stage Volume"].shift(1).fillna(forward_df["Stage Volume"]).astype(int) - forward_df["Stage Volume"]
        if len(losses) > 1:
            fig_pie = px.pie(values=losses[1:].astype(int), names=forward_df["Stage Name"][1:], title="Losses by Stage")
            pie_html = pio.to_html(fig_pie, full_html=False)
        else:
            pie_html = "<div>No losses to display</div>"

        fig_area = px.area(forward_df, x="Stage Name", y="Stage Volume", title="Cumulative Funnel Area")

        # 🔹 EXTRA CHARTS
        fig_scatter = px.scatter(forward_df, x="Stage Name", y="Stage Volume", size="Stage Volume",
                                 color="Stage Name", title="Stage Volumes (Scatter)")

        stacked_df = pd.DataFrame({
            "Stage Name": forward_df["Stage Name"],
            "Forward": forward_df["Stage Volume"],
            "Reverse Required": reverse_df["Required Volume"],
        })
        fig_stacked = px.bar(stacked_df, x="Stage Name", y=["Forward", "Reverse Required"],
                             title="Forward vs Reverse (Stacked)", barmode="stack")

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=revenue_estimate,
            delta={"reference": target_revenue, "increasing": {"color": "green"}},
            gauge={
                "axis": {"range": [0, max(target_revenue, revenue_estimate * 1.2)]},
                "bar": {"color": "blue"},
                "steps": [
                    {"range": [0, target_revenue], "color": "lightgray"},
                    {"range": [target_revenue, max(target_revenue, revenue_estimate * 1.2)], "color": "red"},
                ],
            },
            title={"text": "Revenue vs Target"}
        ))

    except Exception:
        fig_forward = fig_reverse = fig_funnel = fig_line = None
        pie_html = "<div>Chart error</div>"
        fig_area = fig_scatter = fig_stacked = fig_gauge = None

    charts = {
        "Forward Bar": pio.to_html(fig_forward, full_html=False) if fig_forward else "<div/>",
        "Reverse Bar": pio.to_html(fig_reverse, full_html=False) if fig_reverse else "<div/>",
        "Funnel Shape": pio.to_html(fig_funnel, full_html=False) if fig_funnel else "<div/>",
        "Line Drop-off": pio.to_html(fig_line, full_html=False) if fig_line else "<div/>",
        "Losses Pie": pie_html,
        "Cumulative Area": pio.to_html(fig_area, full_html=False) if fig_area else "<div/>",
        "Scatter Plot": pio.to_html(fig_scatter, full_html=False) if fig_scatter else "<div/>",
        "Stacked Bar": pio.to_html(fig_stacked, full_html=False) if fig_stacked else "<div/>",
        "Gauge Chart": pio.to_html(fig_gauge, full_html=False) if fig_gauge else "<div/>",
    }

    required_top = int(round(reverse_df.iloc[0]["Required Volume"])) if not reverse_df.empty else 0

    return render_template(
        "index.html",
        forward_table=forward_df.to_html(index=False, classes="table table-striped"),
        reverse_table=reverse_df.to_html(index=False, classes="table table-striped"),
        customers=customers_display,
        revenue=revenue_estimate,
        customers_float=customers_float,
        customers_needed=customers_needed,
        required_top=required_top,
        stages=stages,
        average_deal_size=average_deal_size,
        target_revenue=target_revenue,
        starting_volume=starting_volume,
        charts=charts,
        stage_count=len(stages),
    )

# main code run area

if __name__ == "__main__":
    app.run(debug=True)