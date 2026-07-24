import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from fontTools.cffLib import width
from plotly.graph_objs.layout.scene import xaxis


def polar_plot(df:pd.DataFrame, r:str, theta:str, color: str | None = None, category_orders: dict | None = None, 
               title: str = "Polar chart", width: int = 500, height: int = 500, labels: dict | None = None) -> go.Figure:
    """
    
    :param df: 
    :param r: 
    :param theta: 
    :param color: 
    :param category_orders: 
    :param title: 
    :param width: 
    :param height: 
    :param labels: 
    :return: 
    """
    
    fig = px.bar_polar(
        df,
        r=r,
        theta=theta,
        color=color,
        category_orders=category_orders,
        title=title,
        width=width,
        height=height,
        labels=labels
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                showticklabels=True,
                tickmode="array",
                tickvals=[1000, 2000, 3000, 4000, 5000],
                ticktext=["", "", "", "4k", "5K"],
                showgrid=True,
                gridcolor="#D1DCE5"
            )
        )
    )

    return fig


def bar_plot(df:pd.DataFrame, x:str, y:str, color: str | None = None, barmode: str | None = None, width: int = 750,
             height: int = 750, title : str | None = None, y_title : str | None = None, x_title : str | None = None, x2 : pd.Series | None = None, y2 : pd.Series | None = None,
             name_trace: str | None = None, xlabel: str | None = None) -> go.Figure:
    """
    
    :param title:
    :param x_title:
    :param height:
    :param width:
    :param df:
    :param x: 
    :param y: 
    :param color: 
    :param barmode: 
    :param y_title:
    :param x2: 
    :param y2: 
    :param name_trace: 
    :param xlabel: 
    :return: 
    """

    fig = px.bar(
        df,
        x=x,
        y=y,
        color=color,
        barmode=barmode,
        width=width,
        height=height,
        title=title
    )

    fig.update_layout(
        yaxis=dict(title=y_title),
        yaxis2=dict(
            overlaying="y",
            side="right"
        ),
        legend=dict(x=1.1, y=0.5),
        xaxis=dict(title=x_title),
    )
    if x2 is not None and y2 is not None:
        fig.add_trace(
            go.Scatter(
                x=x2,
                y=y2,
                mode="lines",
                name=name_trace,
                line=dict(width=3, color="red"),
                yaxis="y2"
            )
        )
    
        years_sorted = sorted(x2.unique(), key=int)
    
        fig.update_xaxes(
            title=xlabel,
            type="category",
            categoryorder="array",
            categoryarray=years_sorted
        )

    return fig


def map_plot(df: pd.DataFrame, lat: str, lon: str, hover_name: str | None = None, 
             color: str | None = None, size: str | None = None, width: int = 750, 
             height: int = 750, title: str | None = None, legend_label: str | None = None) -> go.Figure:

    center = dict(lat=df[lat].mean(), lon=df[lon].mean()) if not df.empty else dict(lat=46.5, lon=2.5)

    fig = px.scatter_map(
        df,
        lat=lat,
        lon=lon,
        hover_name=hover_name,
        color=color,
        size=size,
        size_max=15,
        zoom=3.5,
        center=center,
    )
    if title:
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor="center")
        )
    if legend_label:
        fig.update_legends(title=legend_label, y=0.5, x=1.1)

    fig.update_traces(marker=dict(sizemin=5))

    fig.update_layout(
        uirevision="constant",
        autosize=True,   # laisse le conteneur/pane gérer la taille plutôt qu'une valeur fixe
    )

    return fig


def pie_plot(df: pd.DataFrame, values: str, names: str, color: str | None = None, width: int = 500,
             height: int = 500, title: str | None = None) -> go.Figure:
    fig = px.pie(
        df,
        values=values,
        names=names,
        color=color,
        hole=0.5,
        width=width,
        height=height,
    )
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            xanchor="center"
        )
    )

    fig.update_legends(
        y=0.5,
        x=1.1
    )

    return fig
