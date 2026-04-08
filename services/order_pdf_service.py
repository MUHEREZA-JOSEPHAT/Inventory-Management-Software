import os
from datetime import datetime
from PyQt6.QtCore import QMarginsF
from PyQt6.QtGui import QTextDocument, QTextCursor, QPageLayout
from PyQt6.QtPrintSupport import QPrinter

class OrderPDFService:
    @staticmethod
    def generate_order_pdf(supplier_name, items, grand_total):
        """Generates a professional branded PDF for a bulk order"""
        # Ensure temp directory exists
        temp_dir = "temp_orders"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"BulkOrder_{supplier_name.replace(' ', '_')}_{timestamp}.pdf"
        file_path = os.path.join(os.getcwd(), temp_dir, filename)
        
        # HTML Content for the PDF
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #333; }}
                .header {{ text-align: center; border-bottom: 2px solid #2ecc71; padding-bottom: 20px; }}
                .branding {{ color: #2ecc71; font-size: 28px; font-weight: bold; margin-bottom: 5px; }}
                .subtitle {{ color: #7f8c8d; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; }}
                .order-info {{ margin-top: 30px; margin-bottom: 30px; }}
                .order-info td {{ padding: 5px; }}
                table.items {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                table.items th {{ background-color: #f8f9fa; border-bottom: 2px solid #dee2e6; padding: 12px; text-align: left; }}
                table.items td {{ padding: 12px; border-bottom: 1px solid #dee2e6; }}
                .total-row {{ font-size: 18px; font-weight: bold; color: #2ecc71; text-align: right; padding-top: 20px; }}
                .footer {{ text-align: center; margin-top: 50px; font-size: 12px; color: #95a5a6; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="branding">5 STAR SUPERMARKET</div>
                <div class="subtitle">Official Procurement Order</div>
            </div>
            
            <div class="order-info">
                <table width="100%">
                    <tr>
                        <td><strong>To:</strong> {supplier_name}</td>
                        <td align="right"><strong>Date:</strong> {datetime.now().strftime("%B %d, %Y")}</td>
                    </tr>
                    <tr>
                        <td><strong>Ref:</strong> ORD-{"".join([str(ord(c))[:2] for c in supplier_name[:2]])}-{timestamp[:8]}</td>
                    </tr>
                </table>
            </div>
            
            <table class="items">
                <thead>
                    <tr>
                        <th>Product Description</th>
                        <th>Type</th>
                        <th>Qty</th>
                        <th>Unit Price</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for item in items:
            type_text = "New" if item.get('is_new') else "Restock"
            html += f"""
                    <tr>
                        <td>{item['name']}</td>
                        <td>{type_text}</td>
                        <td>{item['qty']}</td>
                        <td>${item['price']:,.2f}</td>
                        <td>${item['total']:,.2f}</td>
                    </tr>
            """
            
        html += f"""
                </tbody>
            </table>
            
            <div class="total-row">Grand Total: ${grand_total:,.2f}</div>
            
            <div class="footer">
                This is a computer-generated document. Authorized signature may be required for processing.<br>
                Thank you for your partnership.
            </div>
        </body>
        </html>
        """
        
        # Generate PDF using QTextDocument and QPrinter
        doc = QTextDocument()
        doc.setHtml(html)
        
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)
        
        # Correctly set margins using QPageLayout and QMarginsF
        margin = doc.documentMargin()
        page_layout = printer.pageLayout()
        page_layout.setMargins(QMarginsF(margin, margin, margin, margin))
        printer.setPageLayout(page_layout)
        
        doc.print(printer)
        
        return file_path
