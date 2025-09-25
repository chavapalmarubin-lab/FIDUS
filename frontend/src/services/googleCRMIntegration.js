/**
 * CLEAN GOOGLE API INTEGRATION FOR CRM
 * Connects all CRM functionality to Google services
 */

import apiAxios from '../utils/apiAxios';

class GoogleCRMIntegration {
  constructor() {
    this.baseUrl = process.env.REACT_APP_BACKEND_URL;
  }

  // ==================== CONNECTION TEST ====================
  
  async testConnection() {
    try {
      console.log('🧪 Testing Google API connection...');
      const response = await apiAxios.get('/google/test-connection');
      console.log('✅ Google API connection test result:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Google API connection test failed:', error);
      return { success: false, error: error.message };
    }
  }

  // ==================== EMAIL INTEGRATION ====================
  
  async sendProspectEmail(prospectEmail, emailType = 'general', customData = {}) {
    try {
      console.log(`📧 Sending ${emailType} email to prospect: ${prospectEmail}`);
      
      const payload = {
        prospect_email: prospectEmail,
        email_type: emailType,
        subject: customData.subject,
        body: customData.body,
        prospect_name: customData.prospectName
      };

      const response = await apiAxios.post('/crm/send-prospect-email', payload);
      console.log('✅ Prospect email sent successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to send prospect email:', error);
      return { success: false, error: error.message };
    }
  }

  async sendClientEmail(clientEmail, subject, body) {
    try {
      console.log(`📧 Sending email to client: ${clientEmail}`);
      
      const payload = {
        to_email: clientEmail,
        subject: subject,
        body: body,
        from_email: 'noreply@fidus.com'
      };

      const response = await apiAxios.post('/google/send-email', payload);
      console.log('✅ Client email sent successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to send client email:', error);
      return { success: false, error: error.message };
    }
  }

  // ==================== MEETING INTEGRATION ====================
  
  async scheduleProspectMeeting(prospectData, meetingData) {
    try {
      console.log(`📅 Scheduling meeting with prospect: ${prospectData.email}`);
      
      const payload = {
        prospect_email: prospectData.email,
        prospect_name: prospectData.name,
        title: meetingData.title || `FIDUS Meeting with ${prospectData.name}`,
        description: meetingData.description || 'Investment consultation meeting',
        start_time: meetingData.startTime,
        end_time: meetingData.endTime
      };

      const response = await apiAxios.post('/crm/schedule-prospect-meeting', payload);
      console.log('✅ Prospect meeting scheduled successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to schedule prospect meeting:', error);
      return { success: false, error: error.message };
    }
  }

  async createGeneralMeeting(title, description, attendeeEmails, startTime, endTime) {
    try {
      console.log(`📅 Creating general meeting: ${title}`);
      
      const payload = {
        title,
        description,
        attendee_emails: attendeeEmails,
        start_time: startTime,
        end_time: endTime
      };

      const response = await apiAxios.post('/google/create-meeting', payload);
      console.log('✅ General meeting created successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to create general meeting:', error);
      return { success: false, error: error.message };
    }
  }

  // ==================== DATA FETCHING ====================
  
  async getEmails(maxResults = 10) {
    try {
      console.log(`📬 Fetching ${maxResults} recent emails...`);
      const response = await apiAxios.get(`/google/emails?max_results=${maxResults}`);
      console.log('✅ Emails fetched successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to fetch emails:', error);
      return { success: false, error: error.message };
    }
  }

  async getDriveFiles(maxResults = 10) {
    try {
      console.log(`📂 Fetching ${maxResults} Drive files...`);
      const response = await apiAxios.get(`/google/drive-files?max_results=${maxResults}`);
      console.log('✅ Drive files fetched successfully:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Failed to fetch Drive files:', error);
      return { success: false, error: error.message };
    }
  }

  // ==================== CRM SPECIFIC ACTIONS ====================
  
  async sendWelcomeEmailToProspect(prospect) {
    return this.sendProspectEmail(prospect.email, 'welcome', {
      prospectName: prospect.name,
      subject: `Welcome to FIDUS Investment Management, ${prospect.name}!`,
      body: `
        <html>
        <body>
        <h2>Welcome to FIDUS Investment Management</h2>
        <p>Dear ${prospect.name},</p>
        <p>Thank you for your interest in our investment services. We are excited to help you achieve your financial goals.</p>
        <p>Our team will be in touch with you shortly to discuss your investment needs.</p>
        <br>
        <p>Best regards,<br>
        The FIDUS Investment Team<br>
        Email: info@fidus.com<br>
        Phone: +1 (555) 123-4567</p>
        </body>
        </html>
      `
    });
  }

  async sendDocumentRequestToProspect(prospect, documentType = 'general') {
    const documentMessages = {
      'aml_kyc': 'We need your AML/KYC documentation to proceed with your investment application.',
      'general': 'We need some additional documents to process your application.',
      'investment_agreement': 'Please review and sign the investment agreement attached.'
    };

    return this.sendProspectEmail(prospect.email, 'document_request', {
      prospectName: prospect.name,
      subject: `Document Request - ${prospect.name}`,
      body: `
        <html>
        <body>
        <h2>Document Request</h2>
        <p>Dear ${prospect.name},</p>
        <p>${documentMessages[documentType]}</p>
        <p>Please upload the required documents to our secure portal or reply to this email with the documents attached.</p>
        <br>
        <p>If you have any questions, please don't hesitate to contact us.</p>
        <br>
        <p>Best regards,<br>
        The FIDUS Investment Team<br>
        Email: info@fidus.com<br>
        Phone: +1 (555) 123-4567</p>
        </body>
        </html>
      `
    });
  }

  async sendInvestmentReportToProspect(prospect, reportData) {
    return this.sendProspectEmail(prospect.email, 'investment_report', {
      prospectName: prospect.name,
      subject: `Your Investment Report - ${prospect.name}`,
      body: `
        <html>
        <body>
        <h2>Your Personalized Investment Report</h2>
        <p>Dear ${prospect.name},</p>
        <p>Please find your personalized investment report below:</p>
        
        <div style="background: #f5f5f5; padding: 15px; margin: 10px 0;">
        <h3>Investment Summary</h3>
        <p><strong>Recommended Portfolio:</strong> ${reportData?.portfolio || 'Diversified Growth Portfolio'}</p>
        <p><strong>Risk Level:</strong> ${reportData?.riskLevel || 'Moderate'}</p>
        <p><strong>Expected Returns:</strong> ${reportData?.expectedReturns || '8-12% annually'}</p>
        </div>
        
        <p>We believe this investment strategy aligns perfectly with your financial goals and risk tolerance.</p>
        <p>Let's schedule a call to discuss this report in detail.</p>
        <br>
        <p>Best regards,<br>
        The FIDUS Investment Team<br>
        Email: info@fidus.com<br>
        Phone: +1 (555) 123-4567</p>
        </body>
        </html>
      `
    });
  }
}

// Export singleton instance
const googleCRMIntegration = new GoogleCRMIntegration();
export default googleCRMIntegration;