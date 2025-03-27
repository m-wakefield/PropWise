import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Real Estate Multi-Property Analyzer", layout="wide")
st.title("🏠 Real Estate Multi-Property Investment Analyzer")

st.info("📱 On mobile? Tap the top-left menu ☰ to enter property info.")

# Initialize session state for properties
if "properties" not in st.session_state:
    st.session_state.properties = []

st.sidebar.header("📋 Enter Property Info")
st.sidebar.markdown("👈 Fill in the fields below and click 'Add Property'.")

# Inputs
name = st.sidebar.text_input("Property Name", value="Property A")
address = st.sidebar.text_input("Address", value="123 Main St")
image_url = st.sidebar.text_input("Image URL (optional)", value="")

sqft = st.sidebar.number_input("Square Footage", value=1500)
price = st.sidebar.number_input("Purchase Price ($)", value=200000)
down = st.sidebar.number_input("Down Payment ($)", value=40000)
interest = st.sidebar.number_input("Interest Rate (%)", value=6.5)
loan_term = st.sidebar.number_input("Loan Term (years)", value=30)
tax = st.sidebar.number_input("Annual Property Tax ($)", value=3600)
insurance = st.sidebar.number_input("Annual Insurance ($)", value=1200)
maint = st.sidebar.number_input("Monthly Maintenance ($)", value=150)
vacancy = st.sidebar.slider("Vacancy Rate (%)", min_value=0, max_value=20, value=5)

rent_est = st.sidebar.number_input("Expected Monthly Rent ($)", value=1800)
appreciation = st.sidebar.number_input("Annual Appreciation (%)", value=3.0)
hold = st.sidebar.number_input("Hold Period (years)", value=5)

rehab = st.sidebar.number_input("Rehab Cost ($)", value=30000)
resale = st.sidebar.number_input("Target Resale Price ($)", value=275000)

# Add property button
if st.sidebar.button("Add Property"):
    st.session_state.properties.append({
        "Name": name,
        "Address": address,
        "Image": image_url,
        "SqFt": sqft,
        "Price": price,
        "Down": down,
        "Interest": interest,
        "LoanTerm": loan_term,
        "Tax": tax,
        "Insurance": insurance,
        "Maint": maint,
        "Vacancy": vacancy / 100,
        "Rent": rent_est,
        "Appreciation": appreciation,
        "Hold": hold,
        "Rehab": rehab,
        "Resale": resale
    })

# Display all properties
if st.session_state.properties:
    st.subheader("📊 Property Comparison")

    comparison_data = []
    for prop in st.session_state.properties:
        loan_amt = prop["Price"] - prop["Down"]
        monthly_interest = prop["Interest"] / 12 / 100
        months = prop["LoanTerm"] * 12
        mortgage = loan_amt * (monthly_interest * (1 + monthly_interest)**months) / ((1 + monthly_interest)**months - 1)

        tax_m = prop["Tax"] / 12
        ins_m = prop["Insurance"] / 12
        total_monthly = mortgage + tax_m + ins_m + prop["Maint"]

        # Adjust rent for vacancy
        net_rent = prop["Rent"] * (1 - prop["Vacancy"])
        cash_flow = net_rent - total_monthly
        annual_cf = cash_flow * 12

        future_value = prop["Price"] * ((1 + prop["Appreciation"] / 100) ** prop["Hold"])
        appreciation_gain = future_value - prop["Price"]
        total_invested = prop["Down"] + (prop["Maint"] * 12 * prop["Hold"])

        roi = ((annual_cf * prop["Hold"]) + appreciation_gain) / total_invested * 100
        flip_profit = prop["Resale"] - prop["Price"] - prop["Rehab"]

        comparison_data.append({
            "Name": prop["Name"],
            "Address": prop["Address"],
            "Image": prop["Image"],
            "Monthly Cost": round(total_monthly, 2),
            "Net Rent": round(net_rent, 2),
            "Cash Flow": round(cash_flow, 2),
            "Annual Profit": round(annual_cf, 2),
            "ROI (%)": round(roi, 2),
            "Flip Profit": round(flip_profit, 2)
        })

    df = pd.DataFrame(comparison_data)

    # Display images + summary
    for i, row in df.iterrows():
        st.markdown(f"### {row['Name']}")
        st.write(f"**Address:** {row['Address']}")
        if row["Image"]:
            st.image(row["Image"], width=400)
        st.write(f"**Monthly Cost:** ${row['Monthly Cost']} | **Net Rent:** ${row['Net Rent']} | **Cash Flow:** ${row['Cash Flow']}")
        st.write(f"**Annual Profit:** ${row['Annual Profit']} | **ROI:** {row['ROI (%)']}% | **Flip Profit:** ${row['Flip Profit']}")
        st.markdown("---")

    # Chart
    st.subheader("📈 ROI Comparison")
    fig, ax = plt.subplots()
    ax.bar(df["Name"], df["ROI (%)"], color="teal")
    ax.set_ylabel("ROI (%)")
    ax.set_title("Return on Investment by Property")
    st.pyplot(fig)

    # Export
    st.subheader("📤 Export to Excel")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Properties")
    st.download_button("Download Excel File", buffer.getvalue(), file_name="multi_property_analysis.xlsx")
else:
    st.warning("No properties added yet. Use the sidebar to input and add a property.")
