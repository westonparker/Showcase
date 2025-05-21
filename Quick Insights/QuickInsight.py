import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


import openai
import os
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Function to see if Excel column is a date column
def detect_date_columns(df):
    date_keywords = ["date", "month", "year", "time", "timestamp", "day", "quarter"]
    likely_date_cols = []

    for col in df.columns:
        col_lower = col.lower()
        if any(keyword in col_lower for keyword in date_keywords):
            likely_date_cols.append(col)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            likely_date_cols.append(col)
        elif pd.api.types.is_object_dtype(df[col]):
            try:
                converted = pd.to_datetime(df[col], errors="coerce")
                if converted.notna().sum() > 0:
                    likely_date_cols.append(col)
            except:
                continue
    return list(set(likely_date_cols))


#On boot up - hopefully
placeholder = st.empty()
placeholder.info("App may take a few seconds to wake up if idle. Thanks for your patience.")
time.sleep(2)
placeholder.empty()

# user options

# Sales
def track_sales_over_time(data):
    date_cols = detect_date_columns(data)

    if not date_cols:
        st.warning("No obvious date column found. Please select one manually.")
        x_col = st.selectbox("Select a date/time column manually", data.columns)
    else:
        x_col = st.selectbox("Select the time column (X-axis)", date_cols, index=0)

    # Try parsing the selected X-axis column as datetime
    data[x_col] = pd.to_datetime(data[x_col], errors='coerce')
    data = data.dropna(subset=[x_col])

    if data[x_col].isna().all():
        st.error(f"The selected column '{x_col}' could not be parsed as dates. Please choose another.")
        return

    numeric_cols = data.select_dtypes(include='number').columns.tolist()
    y_cols = st.multiselect("Select the metric(s) to track (Y-axis)", numeric_cols)

    if not y_cols:
        st.info("Select at least one column to visualize.")
        return

    fig, ax = plt.subplots()
    for col in y_cols:
        ax.plot(data[x_col], data[col], label=col)

    ax.set_xlabel(x_col)
    ax.set_ylabel("Sales")
    ax.set_title("Sales Over Time")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    st.subheader("Analysis (Powered by AI, may take a couple of seconds to load):")

    sample_data = data[[x_col] + y_cols].head(200).to_csv(index=False)

    prompt = f"""
    You are a data analyst. The user uploaded sales data.

    Task: Analyze this sample of the sales data and return high-level business insights.
    Use plain English. Focus on overall trends, interesting comparisons, or anomalies.
    Explain as if talking to a non-technical business user.
    
    Give a "conclusion" at the end, where you give the user a takeway.
    
    If the data is too sparse or not conclusive enough to give the conclusion, say something along the lines of:
    "The Data provided is not dense enough to give a full conclusion, if you could provide more data, this application will
    perform better."


    {sample_data}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        insight = response.choices[0].message.content
        #st.subheader("AI-Generated Insight")
        st.write(insight)
    except Exception as e:
        st.error(f"Error querying OpenAI: {e}")



def compare_products_or_regions(data):
    st.subheader("Compare Products or Regions")

    # Detect categorical columns (objects with a small number of unique values)
    categorical_cols = [col for col in data.columns if data[col].dtype == 'object' and data[col].nunique() <= 50]
    if not categorical_cols:
        st.warning("No suitable category columns found (e.g., product or region).")
        return

    category_col = st.selectbox("Select a category column to compare", categorical_cols)

    numeric_cols = data.select_dtypes(include='number').columns.tolist()
    y_cols = st.multiselect("Select numeric metric(s) to compare", numeric_cols)

    if not y_cols:
        st.info("Please select at least one numeric column.")
        return

    # Plotting
    fig, ax = plt.subplots()
    grouped = data.groupby(category_col)[y_cols].mean().sort_values(by=y_cols[0], ascending=False)
    grouped.plot(kind='bar', ax=ax)
    ax.set_title(f"Average Values by {category_col}")
    ax.set_ylabel("Metric Values")
    ax.set_xlabel(category_col)
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("Analysis (Powered by AI, may take a couple of seconds to load):")

    sample_data = data[[category_col] + y_cols].head(200).to_csv(index=False)

    prompt = f"""
    You are a data analyst. The user uploaded data comparing products or regions.

    Task: Analyze the provided sample data and deliver a comparison between the different categories in the selected column: "{category_col}".
    Use plain English. Focus on differences in performance across the selected metrics.
    Highlight strong performers, weak ones, and anything surprising or inconsistent.

    Give a "conclusion" at the end, summarizing the key takeaway.

    If the data is too sparse or not conclusive enough to give a conclusion, say something along the lines of:
    "The Data provided is not dense enough to give a full conclusion. If you could provide more data, this application will perform better."


    {sample_data}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        insight = response.choices[0].message.content
        st.write(insight)
    except Exception as e:
        st.error(f"Error querying OpenAI: {e}")

def identify_sales_trends(data):
    st.subheader("Identify Sales Trends or Seasonal Patterns")

    # Detect date/time columns
    date_cols = detect_date_columns(data)
    if not date_cols:
        st.warning("No date column detected. Please select one manually.")
        x_col = st.selectbox("Select a date/time column", data.columns)
    else:
        x_col = st.selectbox("Select the time column (X-axis)", date_cols, index=0)

    # Parse date column
    data[x_col] = pd.to_datetime(data[x_col], errors='coerce')
    data = data.dropna(subset=[x_col])

    if data[x_col].isna().all():
        st.error(f"The selected column '{x_col}' could not be parsed as dates.")
        return

    # Let user pick numeric columns
    numeric_cols = data.select_dtypes(include='number').columns.tolist()
    y_cols = st.multiselect("Select metric(s) to analyze for trends", numeric_cols)

    if not y_cols:
        st.info("Please select at least one metric to continue.")
        return

    # Plotting line graphs
    fig, ax = plt.subplots()
    for col in y_cols:
        ax.plot(data[x_col], data[col], label=col)

    ax.set_title("Sales Trends Over Time")
    ax.set_xlabel(x_col)
    ax.set_ylabel("Metric Value")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("Analysis (Powered by AI, may take a couple seconds to load):")

    sample_data = data[[x_col] + y_cols].head(200).to_csv(index=False)

    prompt = f"""
    You are a data analyst. The user uploaded sales data and wants to understand time-based trends.

    Task: Analyze this sample of the sales data to identify any overall trends, patterns, or seasonal behaviors across the selected metrics.
    Use plain English. Mention any increases, decreases, cyclical patterns, or anomalies you observe.

    Conclude with a takeaway that gives the user a clear summary of what the trends suggest.

    If the data is too sparse or unclear, say:
    "The Data provided is not dense enough to give a full conclusion. If you could provide more data, this application will perform better."

    {sample_data}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        insight = response.choices[0].message.content
        st.write(insight)
    except Exception as e:
        st.error(f"Error querying OpenAI: {e}")


# Inventory
def monitor_stock_levels(data):
    st.subheader("Monitor Stock Levels Over Time")

    # Detect date/time columns
    date_cols = detect_date_columns(data)
    if not date_cols:
        st.warning("No date column detected. Please select one manually.")
        x_col = st.selectbox("Select a date/time column", data.columns)
    else:
        x_col = st.selectbox("Select the time column (X-axis)", date_cols, index=0)

    # Parse and validate date column
    data[x_col] = pd.to_datetime(data[x_col], errors='coerce')
    data = data.dropna(subset=[x_col])

    if data[x_col].isna().all():
        st.error(f"The selected column '{x_col}' could not be parsed as dates.")
        return

    # Let user pick numeric columns (stock counts, inventory levels, etc.)
    numeric_cols = data.select_dtypes(include='number').columns.tolist()
    y_cols = st.multiselect("Select stock level column(s) to monitor", numeric_cols)

    if not y_cols:
        st.info("Please select at least one numeric column.")
        return

    # Plot stock levels over time
    fig, ax = plt.subplots()
    for col in y_cols:
        ax.plot(data[x_col], data[col], label=col)

    ax.set_title("Inventory Levels Over Time")
    ax.set_xlabel(x_col)
    ax.set_ylabel("Stock Count")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("Analysis (Powered by AI, may take a couple seconds to load):")

    sample_data = data[[x_col] + y_cols].head(200).to_csv(index=False)

    prompt = f"""
    You are a data analyst. The user uploaded inventory stock level data.

    Task: Analyze the following sample data to describe how inventory levels are changing over time. Look for signs of consistent depletion, restocking events, or patterns in stock behavior.
    Use plain English. Highlight any anomalies, rapid drops, or potential issues in inventory stability.

    End with a clear conclusion that helps the user understand what their stock trends suggest.

    If the data is too sparse or unclear, say:
    "The Data provided is not dense enough to give a full conclusion. If you could provide more data, this application will perform better."


    {sample_data}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        insight = response.choices[0].message.content
        st.write(insight)
    except Exception as e:
        st.error(f"Error querying OpenAI: {e}")


def identify_fast_slow_items(data):
    st.subheader("Identify Fast- and Slow-Moving Inventory Items")

    # Step 1: Category column (e.g., product/SKU)
    cat_cols = [col for col in data.columns if data[col].dtype == 'object' and data[col].nunique() <= 100]
    if not cat_cols:
        st.warning("No suitable item/category columns found.")
        return
    item_col = st.selectbox("Select the item/category column", cat_cols)

    # Step 2: Date column
    date_cols = detect_date_columns(data)
    if not date_cols:
        st.warning("No date column found. Please select one.")
        date_col = st.selectbox("Select a date column", data.columns)
    else:
        date_col = st.selectbox("Select the time/date column", date_cols, index=0)
    data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
    data = data.dropna(subset=[date_col])

    # Step 3: Metric column (sales, stock movement, etc.)
    num_cols = data.select_dtypes(include='number').columns.tolist()
    metric_col = st.selectbox("Select the metric to measure movement (e.g., sales, quantity used)", num_cols)

    # Step 4: Group and aggregate by item
    grouped = data.groupby(item_col)[metric_col].sum().sort_values(ascending=False)
    top_items = grouped.head(10)
    bottom_items = grouped.tail(10)

    # Step 5: Plotting
    fig, ax = plt.subplots()
    grouped.plot(kind='bar', ax=ax)
    ax.set_title("Total Movement by Item")
    ax.set_ylabel("Total Quantity")
    ax.set_xlabel("Item")
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("Analysis (Powered by AI, may take a second to load):")

    sample_data = data[[item_col, metric_col]].head(200).to_csv(index=False)

    prompt = f"""
    You are a data analyst. The user uploaded inventory movement data.

    Task: Review the movement totals of different items and identify which items are fast-moving (high total quantity or frequency) and which are slow-moving.
    Use plain English. Mention any standouts on either end of the spectrum.

    Conclude with a summary that can help the business adjust stocking decisions.

    If the data is too sparse or not conclusive enough, say:
    "The Data provided is not dense enough to give a full conclusion. If you could provide more data, this application will perform better."


    {sample_data}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        insight = response.choices[0].message.content
        st.write(insight)
    except Exception as e:
        st.error(f"Error querying OpenAI: {e}")


def find_stockout_overstock_risks(data):
    st.subheader("Identify Stockout and Overstock Risks")

    # Step 1: Detect product/item column
    cat_cols = [col for col in data.columns if data[col].dtype == 'object' and data[col].nunique() <= 100]
    if not cat_cols:
        st.warning("No suitable item/category columns found.")
        return
    item_col = st.selectbox("Select the item/category column", cat_cols)

    # Step 2: Detect date column
    date_cols = detect_date_columns(data)
    if not date_cols:
        st.warning("No date column found. Please select one.")
        date_col = st.selectbox("Select a date column", data.columns)
    else:
        date_col = st.selectbox("Select the time/date column", date_cols, index=0)
    data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
    data = data.dropna(subset=[date_col])

    # Step 3: Select numeric column (stock level)
    num_cols = data.select_dtypes(include='number').columns.tolist()
    stock_col = st.selectbox("Select the stock level column", num_cols)

    # Step 4: Thresholds
    stockout_threshold = st.number_input("Stockout threshold (≤ this value is a risk)", value=5)
    overstock_threshold = st.number_input("Overstock threshold (≥ this value is a risk)", value=500)

    # Step 5: Latest stock snapshot (most recent date per item)
    latest_stock = data.sort_values(by=date_col).groupby(item_col).tail(1)

    stockout_items = latest_stock[latest_stock[stock_col] <= stockout_threshold]
    overstock_items = latest_stock[latest_stock[stock_col] >= overstock_threshold]

    # Step 6: Plotting
    st.write("📉 Potential Stockouts:")
    if stockout_items.empty:
        st.info("No items are currently below the stockout threshold.")
    else:
        st.dataframe(stockout_items[[item_col, stock_col]])
        fig, ax = plt.subplots()
        ax.bar(stockout_items[item_col], stockout_items[stock_col], color='red')
        ax.set_title("Stockout Risk Items")
        ax.set_ylabel("Stock Level")
        st.pyplot(fig)

    st.write("📦 Potential Overstocks:")
    if overstock_items.empty:
        st.info("No items are currently above the overstock threshold.")
    else:
        st.dataframe(overstock_items[[item_col, stock_col]])
        fig, ax = plt.subplots()
        ax.bar(overstock_items[item_col], overstock_items[stock_col], color='blue')
        ax.set_title("Overstock Risk Items")
        ax.set_ylabel("Stock Level")
        st.pyplot(fig)

    st.subheader("Analysis (Powered by AI, may take a second to load):")

    sample_data = latest_stock[[item_col, stock_col]].head(200).to_csv(index=False)

    prompt = f"""
    You are a data analyst. The user uploaded inventory stock data.

    Task: Identify which items are at risk of stockout (very low stock levels) or overstock (excessively high levels).
    Consider the provided snapshot of current stock levels.

    Use plain English. Mention which items are concerning and why. Recommend what the business might do.

    End with a clear conclusion.

    If the data is too sparse or unclear, say:
    "The Data provided is not dense enough to give a full conclusion. If you could provide more data, this application will perform better."


    {sample_data}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        insight = response.choices[0].message.content
        st.write(insight)
    except Exception as e:
        st.error(f"Error querying OpenAI: {e}")


# Profits
def analyze_profit_trends(data):
    st.subheader("Analyze Profit Trends Over Time")

    # Step 1: Date column
    date_cols = detect_date_columns(data)
    if not date_cols:
        st.warning("No date column detected. Please select one manually.")
        x_col = st.selectbox("Select a date/time column", data.columns)
    else:
        x_col = st.selectbox("Select the time column (X-axis)", date_cols, index=0)

    data[x_col] = pd.to_datetime(data[x_col], errors='coerce')
    data = data.dropna(subset=[x_col])
    if data[x_col].isna().all():
        st.error(f"The selected column '{x_col}' could not be parsed as dates.")
        return

    # Step 2: Profit-related numeric columns
    numeric_cols = data.select_dtypes(include='number').columns.tolist()
    y_cols = st.multiselect("Select profit metric(s) to analyze", numeric_cols)

    if not y_cols:
        st.info("Please select at least one numeric column.")
        return

    # Step 3: Plotting
    fig, ax = plt.subplots()
    for col in y_cols:
        ax.plot(data[x_col], data[col], label=col)

    ax.set_title("Profit Trends Over Time")
    ax.set_xlabel(x_col)
    ax.set_ylabel("Profit")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("Analysis (Powered by AI, may take a second to load):")

    sample_data = data[[x_col] + y_cols].head(200).to_csv(index=False)

    prompt = f"""
    You are a data analyst. The user uploaded profit data over time.

    Task: Analyze this sample of profit data. Identify any trends, growth patterns, declines, or fluctuations.
    Mention if certain periods had spikes or dips. Focus on what a business user would care about.

    Finish with a conclusion that summarizes the overall health of the profit trend.

    If the data is too sparse or unclear, say:
    "The Data provided is not dense enough to give a full conclusion. If you could provide more data, this application will perform better."


    {sample_data}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        insight = response.choices[0].message.content
        st.write(insight)
    except Exception as e:
        st.error(f"Error querying OpenAI: {e}")


def compare_profit_margins(data):
    st.subheader("Compare Profit Margins Across Categories")

    # Step 1: Categorical column selection (e.g., Product, Region)
    cat_cols = [col for col in data.columns if data[col].dtype == 'object' and data[col].nunique() <= 100]
    if not cat_cols:
        st.warning("No suitable category columns found.")
        return
    category_col = st.selectbox("Select a category to compare (e.g., Product, Region)", cat_cols)

    # Step 2: Profit margin column
    numeric_cols = data.select_dtypes(include='number').columns.tolist()
    margin_col = st.selectbox("Select the profit margin column", numeric_cols)

    # Step 3: Aggregate margins by category
    grouped = data.groupby(category_col)[margin_col].mean().sort_values(ascending=False)

    # Step 4: Plot
    fig, ax = plt.subplots()
    grouped.plot(kind='bar', ax=ax)
    ax.set_title(f"Average Profit Margins by {category_col}")
    ax.set_ylabel("Average Profit Margin")
    ax.set_xlabel(category_col)
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("Analysis (Powered by AI, may take a second to load):")

    sample_data = data[[category_col, margin_col]].head(200).to_csv(index=False)

    prompt = f"""
    You are a data analyst. The user uploaded data comparing profit margins across categories.

    Task: Review this sample of profit margin data grouped by category: "{category_col}".
    Identify which categories are the most profitable, which are underperforming, and any notable patterns or inconsistencies.

    Use plain English. Focus on how the business could prioritize or improve different segments.

    Finish with a clear conclusion about where margins are strong or weak.

    If the data is too sparse or unclear, say:
    "The Data provided is not dense enough to give a full conclusion. If you could provide more data, this application will perform better."


    {sample_data}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        insight = response.choices[0].message.content
        st.write(insight)
    except Exception as e:
        st.error(f"Error querying OpenAI: {e}")


def breakdown_profit_by_category(data):
    st.subheader("Break Down Profit by Category")

    # Step 1: Category selection
    cat_cols = [col for col in data.columns if data[col].dtype == 'object' and data[col].nunique() <= 100]
    if not cat_cols:
        st.warning("No suitable category columns found.")
        return
    category_col = st.selectbox("Select a category (e.g., product, region, department)", cat_cols)

    # Step 2: Profit metric
    numeric_cols = data.select_dtypes(include='number').columns.tolist()
    profit_col = st.selectbox("Select the profit column", numeric_cols)

    # Step 3: Grouping
    grouped = data.groupby(category_col)[profit_col].sum().sort_values(ascending=False)

    # Step 4: Plotting
    fig, ax = plt.subplots()
    grouped.plot(kind='bar', ax=ax)
    ax.set_title(f"Total Profit by {category_col}")
    ax.set_ylabel("Total Profit")
    ax.set_xlabel(category_col)
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("Analysis (Powered by AI, may take a second to load):")

    sample_data = data[[category_col, profit_col]].head(200).to_csv(index=False)

    prompt = f"""
    You are a data analyst. The user uploaded data showing total profit by category: "{category_col}".

    Task: Analyze this data and explain which categories contribute the most and least to overall profit.
    Use plain English. Mention any strong or weak performers, imbalances, or potential focus areas.

    End with a summary conclusion to guide business decisions.

    If the data is too sparse or unclear, say:
    "The Data provided is not dense enough to give a full conclusion. If you could provide more data, this application will perform better."


    {sample_data}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        insight = response.choices[0].message.content
        st.write(insight)
    except Exception as e:
        st.error(f"Error querying OpenAI: {e}")

# Losses
def identify_loss_patterns(data):
    st.subheader("Identify Loss Patterns Over Time")

    # Step 1: Date column
    date_cols = detect_date_columns(data)
    if not date_cols:
        st.warning("No date column detected. Please select one manually.")
        x_col = st.selectbox("Select a date/time column", data.columns)
    else:
        x_col = st.selectbox("Select the time column (X-axis)", date_cols, index=0)

    data[x_col] = pd.to_datetime(data[x_col], errors='coerce')
    data = data.dropna(subset=[x_col])
    if data[x_col].isna().all():
        st.error(f"The selected column '{x_col}' could not be parsed as dates.")
        return

    # Step 2: Loss metric(s)
    numeric_cols = data.select_dtypes(include='number').columns.tolist()
    y_cols = st.multiselect("Select loss-related metric(s) to analyze", numeric_cols)

    if not y_cols:
        st.info("Please select at least one numeric column.")
        return

    # Step 3: Plotting
    fig, ax = plt.subplots()
    for col in y_cols:
        ax.plot(data[x_col], data[col], label=col)

    ax.set_title("Loss Trends Over Time")
    ax.set_xlabel(x_col)
    ax.set_ylabel("Loss Amount")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("Analysis (Powered by AI, may take a second to load):")

    sample_data = data[[x_col] + y_cols].head(200).to_csv(index=False)

    prompt = f"""
    You are a data analyst. The user uploaded time-based data on financial or operational losses.

    Task: Analyze the sample data and identify patterns in losses. Look for trends over time — rising, falling, or recurring spikes.
    Note any outliers or periods of abnormal losses.

    Use plain English. Conclude with a short summary explaining what the data suggests and how a business might respond.

    If the data is too sparse or unclear, say:
    "The Data provided is not dense enough to give a full conclusion. If you could provide more data, this application will perform better."


    {sample_data}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        insight = response.choices[0].message.content
        st.write(insight)
    except Exception as e:
        st.error(f"Error querying OpenAI: {e}")


def compare_loss_categories(data):
    st.subheader("Compare Loss Categories")

    # Step 1: Categorical column for grouping
    cat_cols = [col for col in data.columns if data[col].dtype == 'object' and data[col].nunique() <= 100]
    if not cat_cols:
        st.warning("No suitable category columns found.")
        return
    category_col = st.selectbox("Select a loss category column (e.g., type, region, cause)", cat_cols)

    # Step 2: Loss metric
    numeric_cols = data.select_dtypes(include='number').columns.tolist()
    loss_col = st.selectbox("Select the loss amount column", numeric_cols)

    # Step 3: Group and aggregate
    grouped = data.groupby(category_col)[loss_col].sum().sort_values(ascending=False)

    # Step 4: Plot
    fig, ax = plt.subplots()
    grouped.plot(kind='bar', ax=ax)
    ax.set_title(f"Total Loss by {category_col}")
    ax.set_ylabel("Total Loss Amount")
    ax.set_xlabel(category_col)
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("Analysis (Powered by AI, may take a second to load):")

    sample_data = data[[category_col, loss_col]].head(200).to_csv(index=False)

    prompt = f"""
    You are a data analyst. The user uploaded data showing losses grouped by category: "{category_col}".

    Task: Analyze the data and identify which categories are responsible for the highest and lowest losses.
    Use plain English. Mention top loss drivers, any surprising results, and what areas might need further investigation or action.

    End with a conclusion summarizing the key takeaway and what the business should focus on.

    If the data is too sparse or unclear, say:
    "The Data provided is not dense enough to give a full conclusion. If you could provide more data, this application will perform better."


    {sample_data}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        insight = response.choices[0].message.content
        st.write(insight)
    except Exception as e:
        st.error(f"Error querying OpenAI: {e}")


def run_general_insight(data, user_prompt=None):
    st.subheader("AI-Powered Data Insight")

    sample_data = data.head(200).to_csv(index=False)

    # Base prompt
    base_prompt = f"""
    You are a data analyst. The user uploaded a dataset and wants help understanding it.

    Task: Analyze the structure and contents of the dataset and describe any interesting patterns, anomalies, inconsistencies, or potential issues you see.

    Be specific but use plain English. Provide a short conclusion with a business-focused takeaway.

    If the data is too sparse or unclear, say:
    "The Data provided is not dense enough to give a full conclusion. If you could provide more data, this application will perform better."

    
    {sample_data}
    """

    # If user provided a custom prompt, append it
    if user_prompt:
        base_prompt += f"\n\nAdditional instruction from user: {user_prompt}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",

            messages=[{"role": "user", "content": base_prompt}]
        )
        insight = response.choices[0].message.content
        st.write(insight)
    except Exception as e:
        st.error(f"Error querying OpenAI: {e}")


#main function

st.title("Excel Data Analyzer")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])

if uploaded_file:
    sheet_names = pd.ExcelFile(uploaded_file).sheet_names
    selected_sheet = st.selectbox("Choose a sheet", sheet_names)
    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

    st.success(f"Loaded data from '{selected_sheet}'")

    data_type = st.selectbox(
        "What data are you analyzing today?",
        ["Sales", "Inventory", "Profits", "Losses", "Other"]
    )

    analysis_options = {
        "Sales": [
            "Track sales over time",
            "Compare products or regions",
            "Identify sales trends or seasonal patterns"
        ],
        "Inventory": [
            "Monitor stock levels over time",
            "Identify fast- and slow-moving items",
            "Find stockouts or overstock risks"
        ],
        "Profits": [
            "Analyze profit trends",
            "Compare profit margins across products",
            "Break down profit by region or category"
        ],
        "Losses": [
            "Identify loss patterns over time",
            "Compare loss causes or categories",
        ],
        "Other": [
            "Can you find the issues in this Data?",
            "Custom",
        ]
    }

    analysis_goal = st.selectbox(
        "What do you want from this data?",
        analysis_options.get(data_type, [])
    )
    if not analysis_goal:
        st.info("Please select a goal to proceed.")
        st.stop()
    if data_type == "Sales":
        if analysis_goal == "Track sales over time":
            track_sales_over_time(df)
        elif analysis_goal == "Compare products or regions":
            compare_products_or_regions(df)
        elif analysis_goal == "Identify sales trends or seasonal patterns":
            identify_sales_trends(df)

    elif data_type == "Inventory":
        if analysis_goal == "Monitor stock levels over time":
            monitor_stock_levels(df)
        elif analysis_goal == "Identify fast- and slow-moving items":
            identify_fast_slow_items(df)
        elif analysis_goal == "Find stockouts or overstock risks":
            find_stockout_overstock_risks(df)

    elif data_type == "Profits":
        if analysis_goal == "Analyze profit trends":
            analyze_profit_trends(df)
        elif analysis_goal == "Compare profit margins across products":
            compare_profit_margins(df)
        elif analysis_goal == "Break down profit by region or category":
            breakdown_profit_by_category(df)

    elif data_type == "Losses":
        if analysis_goal == "Identify loss patterns over time":
            identify_loss_patterns(df)
        elif analysis_goal == "Compare loss causes or categories":
            compare_loss_categories(df)



    elif data_type == "Other":

        if analysis_goal == "Can you find the issues in this Data?":


            run_general_insight(df, user_prompt=None)

        elif analysis_goal == "Custom":

            user_custom_prompt = st.text_area("What would you like to ask about this data?")

            if st.button("Run Custom Analysis"):

                if user_custom_prompt.strip():

                    run_general_insight(df, user_prompt=user_custom_prompt.strip())

                else:

                    st.warning("Please enter a custom prompt to proceed.")

 