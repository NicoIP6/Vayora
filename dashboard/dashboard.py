import panel as pn
import plotly.express as px
import datetime as dt
from shared.database_file.set_up import Setup
from dashboard.plot_builder import bar_plot, polar_plot, map_plot, pie_plot


def get_direction_data(countries, date_ran, takeoff_type, season):

    countries = [c.lower() for c in countries]
    start_date, end_date = date_ran
    takeoff_type = [tt.lower() for tt in takeoff_type]
    season = [s.lower() for s in season]

    conn = Setup.get_duckdb_conn()

    query = """
    WITH f AS (
        SELECT 
            ROUND(dw.wind_direction_120m, -1) as wind_direction,
            ff.fact_flight_bk as flight,
            CASE
                WHEN ff.fact_flight_distance <=30 
                     OR ff.fact_flight_distance IS NULL THEN '0-30'
                WHEN ff.fact_flight_distance <=50 THEN '31-50'
                WHEN ff.fact_flight_distance <=100 THEN '51-100'
                WHEN ff.fact_flight_distance <=200 THEN '101-200'
                ELSE '200+'
            END AS distance_category
        FROM vayora_dw.fact_flight ff
        JOIN vayora_dw.dim_weather dw ON ff.fact_flight_weather = dw.dim_weather_sk
        JOIN vayora_dw.dim_takeoff dto ON ff.fact_flight_takeoff = dto.dim_takeoff_sk
        JOIN vayora_dw.dim_date dd on ff.fact_flight_start_date = dd.date_key
        WHERE LOWER(dto.dim_takeoff_country) IN (SELECT UNNEST(?)) 
          AND dd.full_date between ? AND ?
          AND LOWER(dto.dim_takeoff_type) in (SELECT UNNEST(?))
          AND LOWER(dd.season) IN (SELECT UNNEST(?))
    )
    SELECT 
        COUNT(*) as number_of_flight,
        wind_direction,
        distance_category
    FROM f
    GROUP BY wind_direction, distance_category
    ORDER BY wind_direction, distance_category
    """

    return conn.execute(query, [countries, start_date, end_date, takeoff_type, season]).df()


def get_year_data(countries,date_ran, takeoff_type, season):

    countries = [c.lower() for c in countries]
    start_date, end_date = date_ran
    takeoff_type = [tt.lower() for tt in takeoff_type]
    season = [s.lower() for s in season]

    conn = Setup.get_duckdb_conn()

    query = """
            SELECT COUNT(ff.fact_flight_bk) as flight_count, DIVIDE(SUM(EXTRACT(EPOCH FROM ff.fact_flight_airtime)), 60) AS airtime_minutes, dd.year_number, dd.season
            FROM vayora_dw.fact_flight ff
            JOIN vayora_dw.dim_date dd ON dd.date_key = ff.fact_flight_start_date
            JOIN vayora_dw.dim_takeoff dto ON ff.fact_flight_takeoff = dto.dim_takeoff_sk
            WHERE LOWER(dto.dim_takeoff_country) IN (SELECT UNNEST(?)) 
              AND dd.full_date BETWEEN ? AND ?
              AND LOWER(dto.dim_takeoff_type) in (SELECT UNNEST(?))
              AND LOWER(dd.season) IN (SELECT UNNEST(?))
            GROUP BY year_number, season
            """
    return conn.execute(query, [countries,start_date,end_date,takeoff_type,season]).df()


def create_yearly_bar(df):

    airtime_by_year = (
        df.groupby("year_number")["airtime_minutes"]
        .mean()
        .reset_index()
    )

    df = df.copy()
    df["year_str"] = df["year_number"].astype(str)
    airtime_by_year["year_str"] = airtime_by_year["year_number"].astype(str)

    return bar_plot(
        df=df,
        x="year_str",
        y="flight_count",
        color="season",
        barmode="group",
        title="Flight count by year and season",
        x2=airtime_by_year["year_str"],
        y2=airtime_by_year["airtime_minutes"],
        name_trace="Mean airtime (minutes)",
        xlabel="Year",
        height=500,
        x_title="Airtime in minutes",
        y_title="Number of flight"
    )


def get_takeoff_data(countries, date_ran, takeoff_type, season):

    countries = [c.lower() for c in countries]
    start_date, end_date = date_ran
    takeoff_type = [tt.lower() for tt in takeoff_type]
    season = [s.lower() for s in season]

    conn = Setup.get_duckdb_conn()

    query = """
            SELECT COUNT(ff.fact_flight_bk) as flight_count, dto.dim_takeoff_name, dto.dim_takeoff_latitude, dto.dim_takeoff_longitude, dto.dim_takeoff_type
            FROM vayora_dw.fact_flight ff
            JOIN vayora_dw.dim_takeoff dto ON dto.dim_takeoff_sk = ff.fact_flight_takeoff
            JOIN vayora_dw.dim_date dd ON dd.date_key = ff.fact_flight_start_date
            WHERE LOWER(dto.dim_takeoff_country) IN (SELECT UNNEST(?)) 
              AND dd.full_date BETWEEN ? AND ?
              AND LOWER(dto.dim_takeoff_type) in (SELECT UNNEST(?))
              AND LOWER(dd.season) IN (SELECT UNNEST(?))
            GROUP BY dto.dim_takeoff_name, dto.dim_takeoff_latitude, dto.dim_takeoff_longitude, dto.dim_takeoff_type
            """
    return conn.execute(query, [countries, start_date,end_date, takeoff_type, season]).df()


def checkbox_dropdown(name, options, value=None):
    """

    Create a checkbox dropdown widget.

    :param name: name displayed on the button and the CheckBoxGroup
    :param options: list of the available options
    :param value : options checked by default (default None : all options checked)
    :return: A tuple with pn.Column() which is the ready to use dropdown object,
             a checkbox which is to access to the value or attached a callback
    """
    if value is None:
        value = options

    checkbox = pn.widgets.CheckBoxGroup(
        name=name,
        options=options,
        value=value,
        inline=False
    )

    button = pn.widgets.Button(name=f"{name} ▾", button_type="default")

    panel_box = pn.Column(
        checkbox,
        visible=False,
        styles={"border": "1px solid #ccc", "padding": "10px", "background": "white"}
    )

    def toggle(event):
        panel_box.visible = not panel_box.visible

    button.on_click(toggle)

    return pn.Column(button, panel_box), checkbox


pn.extension("plotly")

px.defaults.template = "plotly_white"

px.defaults.color_discrete_sequence = [
    "#0F4A80",
    "#1E6BA8",
    "#0F766E",
    "#52B788",
    "#F4A261",
    "#E76F51",
    "#7B5EA7",
    "#5C677D",
]

def create_dashboard():
    date_range = pn.widgets.DateRangePicker(label="Date Range",
                                            value=(dt.date(2017, 1, 1), dt.date.today()),
                                            start=dt.date(2016, 1, 1)
                                            )

    country_dropdown, country_checkbox = checkbox_dropdown(name="Countries",
                                                           options=["be", "ch", "fr", "es", "it"],
                                                           value=["be", "ch", "es", "it"])

    season_dropdown, season_checkbox = checkbox_dropdown(name="Seasons",
                                                         options=["Winter",
                                                                  "Summer",
                                                                  "Autumn",
                                                                  "Spring"
                                                                  ]
                                                         )
    takeoff_type_dropdown, takeoff_type_checkbox = checkbox_dropdown(name="Takeoff Type",
                                                                     options=["Alpes",
                                                                              "Mer",
                                                                              "Mont",
                                                                              "Plaine",
                                                                              "Pyrénées"
                                                                              ]
                                                                     )
    direction_data = pn.bind(
        get_direction_data,
        country_checkbox,
        date_range,
        takeoff_type_checkbox,
        season_checkbox
    )

    polar = pn.bind(
        lambda df: pn.pane.Plotly(
            polar_plot(
                df,
                r="number_of_flight",
                theta="wind_direction",
                color="distance_category",
                category_orders=
                {
                    "distance_category":
                        [
                            "0-30",
                            "31-50",
                            "51-100",
                            "101-200",
                            "200+"
                        ]
                },
                title="Flight Distribution by Wind Direction (10° Rounded)",
                width=650,
                height=650,
                labels=
                {
                    "wind_direction": "Wind Direction",
                    "distance_category": "Distance Category"
                }
            )
        ),
        direction_data
    )

    year_data = pn.bind(get_year_data,
                        country_checkbox,
                        date_range,
                        takeoff_type_checkbox,
                        season_checkbox
                        )

    bar = pn.bind(create_yearly_bar,
                  year_data
                  )

    takeoff_data = pn.bind(get_takeoff_data,
                           country_checkbox,
                           date_range,
                           takeoff_type_checkbox,
                           season_checkbox
                           )

    takeoff_map = pn.bind(
        lambda df: pn.pane.Plotly(
            map_plot(
                df,
                lat="dim_takeoff_latitude",
                lon="dim_takeoff_longitude",
                hover_name="dim_takeoff_name",
                color="dim_takeoff_type",
                size="flight_count",
                width=650,
                height=650,
                title="Takeoff Traffic",
                legend_label="Takeoff Type",
            )
        ),
        takeoff_data)

    takeoff_pie = pn.bind(
        lambda df: pn.pane.Plotly(
            pie_plot(
                df,
                values="flight_count",
                names="dim_takeoff_type",
                color="dim_takeoff_type",
                width=500,
                height=500,
                title="Takeoff type traffic"
            )
        ),
        takeoff_data)
    sidebar = pn.Column(
        date_range,
        country_dropdown,
        season_dropdown,
        takeoff_type_dropdown,
        width=300,
        sizing_mode="fixed"
    )

    # 2. Contenu principal : on le force à s'étirer en largeur
    main_content = pn.FlexBox(
        polar,
        takeoff_map,
        bar,
        takeoff_pie,
        justify_content="space-evenly",  # Espacement harmonieux
        align_content="center",
        sizing_mode="stretch_width"
    )

    # 3. Assemblage global : étirement complet
    layout = pn.Row(
        sidebar,
        main_content,
        sizing_mode="stretch_width",
        align="start" # Aligne les éléments en haut
    )

    return layout

