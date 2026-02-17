from fpdf import FPDF
import os

def create_policy_pdf(filename, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    pdf.output(filename)

def main():
    if not os.path.exists("data/policies"):
        os.makedirs("data/policies")
        
    refund_policy = """
    Company Refund Policy
    
    1. Eligibility for Refunds
    - Customers are eligible for a full refund within 30 days of purchase if they are unsatisfied with the product.
    - To be eligible, the product must be unused and in the same condition that you received it.
    
    2. Non-refundable Items
    - Gift cards
    - Downloadable software products
    - Some health and personal care items
    
    3. Processing Refunds
    - Once your return is received and inspected, we will send you an email to notify you that we have received your returned item.
    - We will also notify you of the approval or rejection of your refund.
    - If you are approved, then your refund will be processed, and a credit will automatically be applied to your credit card or original method of payment, within a certain amount of days.
    
    4. Late or Missing Refunds
    - If you haven't received a refund yet, first check your bank account again.
    - Then contact your credit card company, it may take some time before your refund is officially posted.
    - Next contact your bank. There is often some processing time before a refund is posted.
    - If you've done all of this and you still have not received your refund yet, please contact us at support@example.com.
    """
    
    # Replace smart quotes with straight quotes to avoid encoding issues
    refund_policy = refund_policy.replace(u"\u2018", "'").replace(u"\u2019", "'")
    
    create_policy_pdf("data/policies/refund_policy.pdf", refund_policy)
    print("Dummy policy PDF created successfully.")

if __name__ == '__main__':
    main()
