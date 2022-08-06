import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from PIL import Image
import streamlit as st
image = Image.open('images.png')
st.title("Bond Risk Manager")
st.image(image)
upload_file = st.sidebar.file_uploader('Upload a file containing earthquake data',type={"csv", "txt"})

# options = st.sidebar.radio('Select what you want to display:', ['PSU, FI & Banks','Corporates'])
# df=pd.read_csv(upload_file)
# rating=df["rating"]


if upload_file is not None:
    df=df=pd.read_csv(upload_file)
    op1 = st.selectbox('Choose Rating',['AAA','BBB','BBB-','BBB+','A','A-','A+','AA','AA+','AA-'])
    fi=st.checkbox("PSU, FI & Banks")
    ri=st.checkbox("Corporates")
    if fi and op1=="AAA":
        df1=df[df["segment"]=="PSU, FI & Banks"]
        df1 = df1[df1["rating"] == "AAA"]
        fig=px.line(df1,
                    x=df1["tenor"],
                    y=df1["yield"])
        fig.update_yaxes(visible=True,range=[.06,.12])
        st.plotly_chart(fig)
    if fi and op1 == "BBB":
        df3 = df[df["segment"] == "PSU, FI & Banks"]
        df3 = df3[df3["rating"] == "BBB"]
        fig1 = px.line(df3,
                      x=df3["tenor"],
                      y=df3["yield"])
        fig1.update_yaxes(visible=True,range=[.06,.12])
        fig1.update_traces(line_color="maroon")
        st.plotly_chart(fig1)
    if fi and op1 == "BBB-":
        df4 = df[df["segment"] == "PSU, FI & Banks"]
        df4 = df4[df4["rating"] == "BBB-"]
        fig2 = px.line(df4,
                      x=df4["tenor"],
                      y=df4["yield"])
        fig2.update_yaxes(visible=True, range=[.06, .12])
        fig2.update_traces(line_color="maroon")
        st.plotly_chart(fig2)
    if fi and op1 == "BBB+":
        df5 = df[df["segment"] == "PSU, FI & Banks"]
        df5 = df5[df5["rating"] == "BBB+"]
        fig3 = px.line(df5,
                      x=df5["tenor"],
                      y=df5["yield"])
        fig3.update_yaxes(visible=True, range=[.06, .12])
        fig3.update_traces(line_color="maroon")
        st.plotly_chart(fig3)
    if fi and op1 == "A":
        df6 = df[df["segment"] == "PSU, FI & Banks"]
        df6 = df6[df6["rating"] == "A"]
        fig4 = px.line(df6,
                      x=df6["tenor"],
                      y=df6["yield"])
        fig4.update_yaxes(visible=True, range=[.06, .12])
        fig4.update_traces(line_color="maroon")
        st.plotly_chart(fig4)
    if fi and op1 == "A-":
        df7 = df[df["segment"] == "PSU, FI & Banks"]
        df7 = df7[df7["rating"] == "A-"]
        fig5= px.line(df7,
                      x=df7["tenor"],
                      y=df7["yield"])
        fig5.update_yaxes(visible=True, range=[.06, .12])
        fig5.update_traces(line_color="maroon")
        st.plotly_chart(fig5)
    if fi and op1 == "A+":
        df8 = df[df["segment"] == "PSU, FI & Banks"]
        df8 = df8[df8["rating"] == "A+"]
        fig6= px.line(df8,
                      x=df1["tenor"],
                      y=df1["yield"])
        fig6.update_yaxes(visible=True, range=[.06, .12])
        fig6.update_traces(line_color="maroon")
        st.plotly_chart(fig6)
    if fi and op1 == "AA":
        df9 = df[df["segment"] == "PSU, FI & Banks"]
        df9 = df9[df9["rating"] == "AA"]
        fig7 = px.line(df9,
                      x=df9["tenor"],
                      y=df9["yield"])
        fig7.update_yaxes(visible=True, range=[.06, .12])
        fig7.update_traces(line_color="maroon")
        st.plotly_chart(fig7)
    if fi and op1 == "AA+":
        df10 = df[df["segment"] == "PSU, FI & Banks"]
        df10 = df10[df10["rating"] == "AA+"]
        fig8 = px.line(df10,
                      x=df10["tenor"],
                      y=df10["yield"])
        fig8.update_yaxes(visible=True, range=[.06, .12])
        fig8.update_traces(line_color="maroon")
        st.plotly_chart(fig8)
    if fi and op1 == "AA-":
        df11 = df[df["segment"] == "PSU, FI & Banks"]
        df11 = df11[df11["rating"] == "AA-"]
        fig9 = px.line(df11,
                      x=df11["tenor"],
                      y=df11["yield"])
        fig9.update_yaxes(visible=True, range=[.06, .12])
        fig9.update_traces(line_color="maroon")
        st.plotly_chart(fig9)

    if ri and op1=="AAA":
        df12=df[df["segment"]=="Corporates"]
        df12 = df12[df12["rating"] == "AAA"]
        fig10=px.line(df12,
                    x=df12["tenor"],
                    y=df12["yield"])
        fig10.update_yaxes(visible=True, range=[.06, .12])
        fig10.update_traces(line_color="maroon")
        st.plotly_chart(fig10)
    if ri and op1 == "BBB":
        df13= df[df["segment"] == "Corporates"]
        df13 = df13[df13["rating"] == "BBB"]
        fig11 = px.line(df13,
                      x=df13["tenor"],
                      y=df13["yield"])
        fig11.update_yaxes(visible=True, range=[.06, .12])
        fig11.update_traces(line_color="maroon")
        st.plotly_chart(fig11)
    if ri and op1 == "BBB-":
        df14 = df[df["segment"] == "Corporates"]
        df14 = df14[df14["rating"] == "BBB-"]
        fig12 = px.line(df14,
                      x=df14["tenor"],
                      y=df14["yield"])
        fig12.update_yaxes(visible=True, range=[.06, .12])
        fig12.update_traces(line_color="maroon")
        st.plotly_chart(fig12)
    if ri and op1 == "BBB+":
        df15 = df[df["segment"] == "Corporates"]
        df15 = df15[df15["rating"] == "BBB+"]
        fig13 = px.line(df15,
                      x=df15["tenor"],
                      y=df15["yield"])
        fig13.update_yaxes(visible=True, range=[.06, .12])
        fig13.update_traces(line_color="maroon")
        st.plotly_chart(fig13)
    if ri and op1 == "A":
        df16 = df[df["segment"] == "Corporates"]
        df16 = df16[df16["rating"] == "A"]
        fig14 = px.line(df16,
                      x=df16["tenor"],
                      y=df16["yield"])
        fig14.update_yaxes(visible=True, range=[.06, .12])
        fig14.update_traces(line_color="maroon")
        st.plotly_chart(fig14)
    if ri and op1 == "A-":
        df17 = df[df["segment"] == "Corporates"]
        df17 = df17[df17["rating"] == "A-"]
        fig15= px.line(df17,
                      x=df17["tenor"],
                      y=df17["yield"])
        fig15.update_yaxes(visible=True, range=[.06, .12])
        fig15.update_traces(line_color="maroon")
        st.plotly_chart(fig15)
    if ri and op1 == "A+":
        df18 = df[df["segment"] == "Corporates"]
        df18 = df18[df18["rating"] == "A+"]
        fig16= px.line(df18,
                      x=df18["tenor"],
                      y=df18["yield"])
        fig16.update_yaxes(visible=True, range=[.06, .12])
        fig16.update_traces(line_color="maroon")
        st.plotly_chart(fig16)
    if ri and op1 == "AA":
        df19 = df[df["segment"] == "Corporates"]
        df19 = df19[df19["rating"] == "AA"]
        fig17 = px.line(df19,
                      x=df19["tenor"],
                      y=df19["yield"])
        fig17.update_yaxes(visible=True, range=[.06, .12])
        fig17.update_traces(line_color="maroon")
        st.plotly_chart(fig17)
    if ri and op1 == "AA+":
        df20 = df[df["segment"] == "Corporates"]
        df20 = df20[df20["rating"] == "AA+"]
        fig18 = px.line(df20,
                      x=df20["tenor"],
                      y=df20["yield"])
        fig18.update_yaxes(visible=True, range=[.06, .12])
        fig18.update_traces(line_color="maroon")
        st.plotly_chart(fig18)
    if ri and op1 == "AA-":
        df21 = df[df["segment"] == "Corporates"]
        df21 = df11[df11["rating"] == "AA-"]
        fig19 = px.line(df21,
                      x=df21["tenor"],
                      y=df21["yield"])
        fig19.update_yaxes(visible=True, range=[.06, .12])
        fig19.update_traces(line_color="maroon")
        st.plotly_chart(fig19)
