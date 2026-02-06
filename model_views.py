def corp_view(corp):
    return f"""Name: {corp.name}
Founded: {corp.founded}
Business Model: 
{corp.business_model}
Employee Count: {corp.employee_count}
Revenue: {corp.revenue}
Growth Rate: {corp.growth_rate}
Publicly Traded: {corp.publicly_traded}
Headquarters: {corp.headquarters}
"""