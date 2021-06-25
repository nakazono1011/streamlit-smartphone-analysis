import streamlit as st
import streamlit.components.v1 as components
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use("ggplot")

# initialize
st.set_page_config(page_title=None, page_icon=None, layout='wide', initial_sidebar_state='auto')

# variables
start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).astimezone()
item_condition_dic = {5: "S", 4: "A", 3:"B", 2: "C", 1: "D", 0:"J"}

@st.cache
def load_data():
  # sql = "SELECT * FROM aws_mysql_tables.clean_fleamarket_sales"
  # project_id = ""
  # df = pd.read_gbq(sql, project_id=project_id)
  df=pd.read_pickle("./data/smartphone2.pkl")
  # df=pd.read_csv("./data/smartphone.csv")

  return df

# timeseries plot
def ts_plot(df):
  ts = df.groupby("item_condition").resample("W", on="sales_date").mean()[["price"]]
  ts = pd.pivot_table(ts, index="item_condition", columns="sales_date").stack().reset_index()

  fig, ax = plt.subplots(figsize=(24,4))
  for condition in ts["item_condition"].unique():
      data = ts[ts["item_condition"] == condition].copy()
      ax.plot(data["sales_date"], data["price"], label=item_condition_dic[condition])
      ax.legend()

  return fig

# stacked bar
def stacked_bar_plot(df):
  monthly_counts = df.groupby("item_condition").resample("M", on="sales_date").count().iloc[:, 1].reset_index()
  monthly_counts["sales_date"] = monthly_counts["sales_date"].dt.strftime("%Y-%m")
  monthly_counts = pd.pivot_table(monthly_counts, index="item_condition", columns="sales_date").droplevel(0, axis=1)

  fig, ax = plt.subplots(figsize=(24, 4))
  for i in range(len(monthly_counts)):
      ax.bar(monthly_counts.columns, monthly_counts.iloc[i], bottom=monthly_counts.iloc[:i].sum())
  return fig

def bar_plot(df, column):
  fig, ax = plt.subplots(figsize=(8,4))
  sns.boxplot(df[column], df["price"], sym="", ax=ax)
  return fig

### main
# load data
df = load_data()
df = df[df["sales_date"] >= start_date]

# side bar
st.sidebar.title("機種別に確認する")
brand = st.sidebar.radio(
  "機種",
  ["ALL"] + list(df["brand_name"].value_counts()[:10].index)
)

# body
if brand == "ALL":
  components.html(
    """
    <h1>スマートフォン市場分析</h1>
      <p>過去にネットフリマで取引が行われたスマートフォンデータを分析して公開しました。</p>
      <p>ヤフオク・メルカリ・ラクマなどの出品情報をもとにデータを分析し、可視化を行っています。</p>
      </br>
    <h2>バーチャートレース</h2>

    <p>過去1年間の機種別の出品件数の状況を時間の経過に合わせて可視化したグラフです</p>
    <p>市場の動向や人気の機種が分かります</p>
    <div class="flourish-embed flourish-bar-chart-race" data-src="visualisation/6515499" data-height="100%">
      <script src="https://public.flourish.studio/resources/embed.js"></script>
    </div>

    <h2>出品情報サマリー</h2>
    <p>2020/6/24～2021/6/24 の1年間のサマリー情報です</p>
    <div class="flourish-embed flourish-table" data-src="visualisation/6516515">
      <script src="https://public.flourish.studio/resources/embed.js"></script>
    </div>
    """
    ,height=2000
    ,width=1500
  )
else:
  st.markdown(f"""
  # {brand}
  """)

  volume = st.selectbox(
      "容量を選択してください",
        df[df["brand_name"] == brand]["volume"].unique()
      )

  df_brand = df[(df["brand_name"] == brand) & (df["volume"] == volume)]

  st.markdown(
    """
    ## 成約価格
    """)
  st.pyplot(ts_plot(df_brand))

  st.markdown(
    """
    ## 取引件数
    """)
  st.pyplot(stacked_bar_plot(df_brand))

  st.markdown(
    """
    ## 状態別の価格分布
    """)
  col1, col2 = st.beta_columns(2)

  with col1:
    # st.text(df["sim_free_flg"].value_counts())
    st.markdown(
      """
      ### SIMロック
      """)
    st.pyplot(bar_plot(df_brand, "sim_free_flg"))

  with col2:
    st.markdown(
      """
      ### ネットワーク利用制限
      """)
    # st.text(df["restriction"].value_counts())
    st.pyplot(bar_plot(df_brand, "restriction"))
