#!/usr/bin/env python3
"""Generate FIDUS App Documentation PDF with screenshots and explanations."""
from fpdf import FPDF
from PIL import Image
import os

class FidusPDF(FPDF):
    """Custom PDF class for FIDUS documentation."""
    
    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, 'FIDUS Investment App - Documentation', 0, 0, 'L')
            self.cell(0, 10, f'Page {self.page_no()}', 0, 1, 'R')
            self.line(10, 18, 200, 18)
            self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'Confidential - FIDUS Solutions LLC', 0, 0, 'C')
    
    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 18)
        self.set_text_color(0, 50, 100)
        self.cell(0, 12, title, 0, 1, 'L')
        self.set_draw_color(0, 180, 216)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(6)
    
    def section_text(self, text):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, text)
        self.ln(4)
    
    def bullet_point(self, text):
        self.set_font('Helvetica', '', 11)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, f'  -  {text}')
        self.ln(1)
    
    def add_screenshot(self, image_path, caption="", max_width=80):
        """Add a centered screenshot with optional caption."""
        if not os.path.exists(image_path):
            self.set_font('Helvetica', 'I', 10)
            self.set_text_color(200, 0, 0)
            self.cell(0, 10, f'[Screenshot not found: {image_path}]', 0, 1, 'C')
            return
        
        # Get image dimensions
        img = Image.open(image_path)
        img_w, img_h = img.size
        aspect = img_h / img_w
        
        display_w = max_width
        display_h = display_w * aspect
        
        # Cap height
        if display_h > 180:
            display_h = 180
            display_w = display_h / aspect
        
        # Check if we need a new page
        if self.get_y() + display_h + 20 > 280:
            self.add_page()
        
        # Center the image
        x_pos = (210 - display_w) / 2
        
        # Add a subtle border/shadow effect
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.rect(x_pos - 1, self.get_y() - 1, display_w + 2, display_h + 2)
        
        self.image(image_path, x=x_pos, y=self.get_y(), w=display_w)
        self.set_y(self.get_y() + display_h + 4)
        
        if caption:
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 6, caption, 0, 1, 'C')
            self.ln(4)


def generate_pdf():
    pdf = FidusPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # ===== COVER PAGE =====
    pdf.add_page()
    pdf.ln(40)
    
    # Logo placeholder - draw FIDUS branding
    pdf.set_fill_color(10, 15, 26)
    pdf.rect(55, 40, 100, 50, 'F')
    pdf.set_font('Helvetica', 'B', 36)
    pdf.set_text_color(0, 180, 216)
    pdf.set_y(52)
    pdf.cell(0, 20, 'FIDUS', 0, 1, 'C')
    pdf.set_font('Helvetica', '', 14)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, 'Investment Portal', 0, 1, 'C')
    
    pdf.ln(20)
    pdf.set_font('Helvetica', 'B', 24)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 12, 'Mobile Application', 0, 1, 'C')
    pdf.set_font('Helvetica', '', 16)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, 'Functional Documentation', 0, 1, 'C')
    
    pdf.ln(10)
    pdf.set_draw_color(0, 180, 216)
    pdf.set_line_width(1)
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    
    pdf.ln(15)
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, 'Version 2.0.0', 0, 1, 'C')
    pdf.cell(0, 8, 'Platforms: iOS & Android', 0, 1, 'C')
    pdf.cell(0, 8, 'Languages: English & Spanish', 0, 1, 'C')
    
    pdf.ln(20)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, 'FIDUS Solutions LLC', 0, 1, 'C')
    pdf.cell(0, 8, 'Saint Kitts and Nevis', 0, 1, 'C')
    
    # ===== TABLE OF CONTENTS =====
    pdf.add_page()
    pdf.chapter_title('Table of Contents')
    pdf.ln(4)
    
    toc_items = [
        ('1. Overview', 'Application summary and key features'),
        ('2. Login Screen', 'Secure authentication with bilingual support'),
        ('3. Dashboard', 'Portfolio overview, balance, and transactions'),
        ('4. Investment Simulator', 'Projected returns calculator'),
        ('5. Product Information', 'FIDUS CORE product details and FAQ'),
        ('6. Settings & Profile', 'Account management and preferences'),
        ('7. Terms & Conditions', 'Mandatory 3-step acceptance flow'),
        ('8. Admin: Terms Log', 'Compliance tracking for acceptances'),
        ('9. Technical Architecture', 'Technology stack and security'),
    ]
    
    for title, desc in toc_items:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(0, 50, 100)
        pdf.cell(0, 8, title, 0, 1)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, f'   {desc}', 0, 1)
        pdf.ln(2)
    
    # ===== 1. OVERVIEW =====
    pdf.add_page()
    pdf.chapter_title('1. Overview')
    pdf.section_text(
        'The FIDUS Investment App is a mobile application designed for retail investors '
        'to manage their investment portfolio with FIDUS Solutions LLC. The app provides '
        'a comprehensive, secure, and user-friendly interface for monitoring investments, '
        'viewing returns, and managing account settings.'
    )
    
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 10, 'Key Features', 0, 1)
    pdf.ln(2)
    
    features = [
        'Bilingual Interface - Full support for English and Spanish',
        'Secure Login - Email/password authentication with biometric support',
        'Real-Time Dashboard - Portfolio balance, earnings, charts, and transactions',
        'Investment Simulator - Calculate projected returns for additional deposits',
        'Product Information - Complete FIDUS CORE investment product details',
        'Terms & Conditions - Mandatory 3-step legal compliance acceptance',
        'Admin Compliance Log - Timestamped record of all T&C acceptances',
        'Profile Management - Edit profile, change language, notification settings',
        'Payment Schedule - Monthly return tracking and payment status',
    ]
    
    for f in features:
        pdf.bullet_point(f)
    
    pdf.ln(6)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 10, 'Platform Availability', 0, 1)
    pdf.section_text(
        'The FIDUS app is built using React Native with Expo, ensuring native performance '
        'on both iOS (iPhone) and Android devices. The app follows platform-specific design '
        'guidelines while maintaining a consistent FIDUS brand experience.'
    )
    
    # ===== 2. LOGIN SCREEN =====
    pdf.add_page()
    pdf.chapter_title('2. Login Screen')
    pdf.section_text(
        'The login screen is the entry point of the application. It features the '
        'prominent FIDUS logo displayed within a white frame for maximum brand visibility '
        'against the dark theme. Users authenticate with their registered email and password.'
    )
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 8, 'Features:', 0, 1)
    pdf.ln(2)
    pdf.bullet_point('FIDUS branded logo with white frame for visibility')
    pdf.bullet_point('Email and password fields with secure text entry')
    pdf.bullet_point('Show/hide password toggle')
    pdf.bullet_point('Biometric login support (Face ID / Touch ID on supported devices)')
    pdf.bullet_point('Link to open a new account at LUCRUM Capital')
    pdf.bullet_point('Full bilingual support (English / Spanish)')
    pdf.ln(4)
    
    pdf.add_screenshot('/app/screenshots/01_login.png', 'Figure 1: Login Screen with FIDUS Logo', max_width=70)
    
    # ===== 3. DASHBOARD =====
    pdf.add_page()
    pdf.chapter_title('3. Dashboard')
    pdf.section_text(
        'The main dashboard provides a comprehensive overview of the investor\'s portfolio. '
        'Upon successful login (and T&C acceptance), users are presented with their current '
        'balance, earnings, portfolio performance chart, quick actions, and recent transactions.'
    )
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 8, 'Dashboard Components:', 0, 1)
    pdf.ln(2)
    pdf.bullet_point('Welcome Header - Personalized greeting with FIDUS logo')
    pdf.bullet_point('Balance Card - Total balance, total earnings, and product badges')
    pdf.bullet_point('Quick Actions - Add Money, Withdraw, Product Info, Simulator')
    pdf.bullet_point('Portfolio Performance Chart - 6-month bar chart with balance trends')
    pdf.bullet_point('Next Payment - Estimated monthly return with end-of-month date')
    pdf.bullet_point('Recent Transactions - Latest 3 transactions with type indicators')
    pdf.bullet_point('Payment Schedule - Monthly payment tracking with funded/pending status')
    pdf.ln(4)
    
    pdf.add_screenshot('/app/screenshots/02_dashboard.png', 'Figure 2: Main Dashboard', max_width=70)
    
    # ===== 4. INVESTMENT SIMULATOR =====
    pdf.add_page()
    pdf.chapter_title('4. Investment Simulator')
    pdf.section_text(
        'The Investment Simulator allows users to explore projected returns based on different '
        'additional deposit amounts. Users can select from predefined deposit options ($500, '
        '$1,000, $5,000, $10,000, $25,000) or enter a custom amount to see how their monthly '
        'and annual returns would change.'
    )
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 8, 'Simulator Features:', 0, 1)
    pdf.ln(2)
    pdf.bullet_point('Predefined deposit amounts for quick selection')
    pdf.bullet_point('Side-by-side comparison: Current vs. New monthly returns')
    pdf.bullet_point('Side-by-side comparison: Current vs. New annual returns')
    pdf.bullet_point('Return rate of 1.5% monthly (18% annual target) clearly displayed')
    pdf.bullet_point('Disclaimer about projected returns at the bottom')
    pdf.ln(4)
    
    pdf.add_screenshot('/app/screenshots/03_invest.png', 'Figure 3: Investment Simulator', max_width=70)
    
    # ===== 5. PRODUCT INFO =====
    pdf.add_page()
    pdf.chapter_title('5. Product Information')
    pdf.section_text(
        'The Info screen provides detailed information about the FIDUS CORE retail investment '
        'product. It answers the most common investor questions in a clean, expandable FAQ format.'
    )
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 8, 'Information Covered:', 0, 1)
    pdf.ln(2)
    pdf.bullet_point('What is the return? - 1.5% monthly on capital (18% annual target)')
    pdf.bullet_point('Minimum investment? - $100 USD with no maximum')
    pdf.bullet_point('Can I withdraw anytime? - No contracts, no lock-in period')
    pdf.bullet_point('Where is my money? - In YOUR LUCRUM broker account')
    pdf.bullet_point('How does FIDUS make money? - Spread between gross and net returns')
    pdf.bullet_point('What are the risks? - Full risk disclosure with Hull Framework')
    pdf.ln(4)
    
    pdf.add_screenshot('/app/screenshots/04_info.png', 'Figure 4: FIDUS CORE Product Information', max_width=70)
    
    # ===== 6. SETTINGS =====
    pdf.add_page()
    pdf.chapter_title('6. Settings & Profile')
    pdf.section_text(
        'The Settings screen provides access to all account management features including '
        'profile editing, language preferences, security settings, notifications, and more.'
    )
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 8, 'Available Settings:', 0, 1)
    pdf.ln(2)
    pdf.bullet_point('Profile - View and edit personal information')
    pdf.bullet_point('Language - Switch between English and Spanish instantly')
    pdf.bullet_point('Security - Change password, enable/disable biometric login')
    pdf.bullet_point('Notifications - Configure notification preferences')
    pdf.bullet_point('Transaction History - View complete transaction log')
    pdf.bullet_point('Terms Acceptances Log - Admin view of compliance records')
    pdf.bullet_point('Withdraw Funds - Initiate withdrawal requests')
    pdf.bullet_point('Go to LUCRUM - Direct link to LUCRUM Capital platform')
    pdf.bullet_point('Logout - Secure sign-out with confirmation')
    pdf.ln(4)
    
    pdf.add_screenshot('/app/screenshots/05_settings.png', 'Figure 5: Settings & Profile Management', max_width=70)
    
    # ===== 7. TERMS & CONDITIONS =====
    pdf.add_page()
    pdf.chapter_title('7. Terms & Conditions')
    pdf.section_text(
        'A mandatory Terms & Conditions acceptance flow is required before users can access '
        'the main application. This is a blocking screen that ensures legal and regulatory '
        'compliance. Users must individually accept three separate sets of terms.'
    )
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 8, 'Three Required Acceptances:', 0, 1)
    pdf.ln(2)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 7, '1. Lucrum Capital Limited - Client Agreement & Risk Disclosures', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 5, '   Covers execution-only service, account types, leverage, margin, segregated funds, fees, AML/KYC requirements, and governing law under FSC Mauritius.')
    pdf.ln(3)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 7, '2. FIDUS Solutions LLC - Money Manager & IB Disclosures', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 5, '   Covers regulatory status, no guarantee of returns, past performance disclaimer, risk disclosures, investor suitability, and restricted jurisdictions.')
    pdf.ln(3)
    
    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 7, '3. Copy Trading Investor Participation Agreement & LPOA', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 5, '   Covers Limited Power of Attorney for copy trading, nature of relationship, fees, activation/termination, limitation of liability, and indemnification.')
    pdf.ln(4)
    
    pdf.section_text(
        'Each section is expandable so users can read the full legal text before accepting. '
        'The "Accept & Continue" button only becomes active after all three checkboxes are '
        'checked. All acceptances are timestamped and logged for compliance purposes.'
    )
    
    pdf.add_screenshot('/app/screenshots/06_terms.png', 'Figure 6: Terms & Conditions Acceptance Flow', max_width=70)
    
    # ===== 8. ADMIN TERMS LOG =====
    pdf.add_page()
    pdf.chapter_title('8. Admin: Terms Acceptances Log')
    pdf.section_text(
        'The Terms Acceptances Log is an administrative view that displays a complete audit '
        'trail of all user T&C acceptances. This provides a compliance record showing who '
        'accepted terms, when they accepted, and which specific terms were acknowledged.'
    )
    
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 8, 'Log Information Displayed:', 0, 1)
    pdf.ln(2)
    pdf.bullet_point('Total count of acceptances')
    pdf.bullet_point('User email for each acceptance record')
    pdf.bullet_point('Individual status for LUCRUM, FIDUS, and Copy Trading terms')
    pdf.bullet_point('Timestamp of acceptance (date and time)')
    pdf.bullet_point('User agent (device/platform identifier)')
    pdf.ln(4)
    
    pdf.add_screenshot('/app/screenshots/07_terms_log.png', 'Figure 7: Admin Terms Acceptances Log', max_width=70)
    
    # ===== 9. TECHNICAL ARCHITECTURE =====
    pdf.add_page()
    pdf.chapter_title('9. Technical Architecture')
    
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 10, 'Technology Stack', 0, 1)
    pdf.ln(2)
    
    tech_items = [
        ('Frontend:', 'React Native with Expo (iOS & Android)'),
        ('Backend:', 'Python FastAPI REST API'),
        ('Database:', 'MongoDB with Motor async driver'),
        ('Navigation:', 'Expo Router (file-based routing)'),
        ('Auth:', 'JWT token-based authentication with bcrypt password hashing'),
        ('State:', 'React Context API for global state management'),
        ('i18n:', 'Custom bilingual system (English / Spanish)'),
        ('Charts:', 'Native React Native bar chart rendering'),
    ]
    
    for label, value in tech_items:
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(35, 7, label, 0, 0)
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(0, 7, value, 0, 1)
    
    pdf.ln(6)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 10, 'Security Features', 0, 1)
    pdf.ln(2)
    pdf.bullet_point('Passwords hashed with bcrypt (never stored in plain text)')
    pdf.bullet_point('JWT tokens for API authentication with expiration')
    pdf.bullet_point('Biometric authentication support (Face ID / Touch ID)')
    pdf.bullet_point('Segregated API architecture with protected endpoints')
    pdf.bullet_point('Secure token storage using AsyncStorage')
    
    pdf.ln(6)
    pdf.set_font('Helvetica', 'B', 13)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 10, 'API Endpoints', 0, 1)
    pdf.ln(2)
    
    endpoints = [
        ('POST /api/auth/login', 'User authentication'),
        ('GET /api/user/profile', 'Retrieve user profile data'),
        ('POST /api/user/accept-terms', 'Record T&C acceptance'),
        ('GET /api/portfolio/history', 'Portfolio performance data'),
        ('GET /api/transactions', 'Transaction history'),
        ('GET /api/admin/terms-acceptances', 'Admin T&C log'),
    ]
    
    for endpoint, desc in endpoints:
        pdf.set_font('Courier', '', 10)
        pdf.set_text_color(0, 100, 150)
        pdf.cell(70, 6, endpoint, 0, 0)
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 6, f'- {desc}', 0, 1)
    
    # ===== CLOSING PAGE =====
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font('Helvetica', 'B', 20)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 12, 'Thank You', 0, 1, 'C')
    
    pdf.ln(10)
    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 7, 
        'For questions or support regarding the FIDUS Investment App, '
        'please contact FIDUS Solutions LLC.',
        align='C'
    )
    
    pdf.ln(15)
    pdf.set_draw_color(0, 180, 216)
    pdf.set_line_width(0.5)
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    
    pdf.ln(15)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(0, 180, 216)
    pdf.cell(0, 8, 'FIDUS Solutions LLC', 0, 1, 'C')
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, 'Saint Kitts and Nevis', 0, 1, 'C')
    pdf.cell(0, 7, '@getfidus', 0, 1, 'C')
    
    # Save PDF
    output_path = '/app/FIDUS_App_Documentation.pdf'
    pdf.output(output_path)
    
    file_size = os.path.getsize(output_path)
    print(f"\nPDF generated successfully!")
    print(f"  Path: {output_path}")
    print(f"  Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"  Pages: {pdf.page_no()}")
    
    return output_path

if __name__ == '__main__':
    generate_pdf()
