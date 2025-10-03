# 📧 Email Automation Dashboard

A simple web application for sending personalized emails at scale. Perfect for job seekers, marketers, and anyone who needs to send automated emails.

## 🚀 Quick Start

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
Go to: `http://localhost:5001`

## 📋 What You Need

- **Python 3.8+** ([Download here](https://python.org))
- **Email account** (Gmail, Outlook, Yahoo, etc.)
- **Contact list** (CSV file with names and emails)

## 🎯 How to Use

### Step 1: Configure Your Email
1. Go to **Configure** page
2. Enter your email and app password
3. Test the connection

### Step 2: Upload Your Contact List
1. Go to **Upload CSV** page
2. Upload your CSV file with contacts
3. Preview your data

### Step 3: Start Your Campaign
1. Go to **Campaign** page
2. Configure settings (test mode recommended first)
3. Start sending emails!

## 📧 Email Provider Setup

### Gmail (Most Popular)
1. Enable 2-Factor Authentication
2. Create App Password: [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Use the app password (not your regular password)

### Outlook/Hotmail
1. Enable 2-Factor Authentication
2. Create App Password: [Microsoft Security](https://account.microsoft.com/security)
3. Use the app password

## 📊 CSV Format

Create a CSV file with these columns:

```csv
company_name,role,recruiter_email,recruiter_first_name
Google,Software Engineer,john@google.com,John
Microsoft,Developer,sarah@microsoft.com,Sarah
Amazon,Data Scientist,mike@amazon.com,Mike
```

## ✨ Features

- 🎯 **Easy Setup**: Simple email configuration
- 📊 **CSV Management**: Upload and validate contact lists
- ✉️ **Email Templates**: Customize your email content
- 📄 **Resume Attachments**: Automatically attach resumes
- 🚀 **Campaign Management**: Start, stop, and monitor campaigns
- 📈 **Real-time Progress**: Live updates during email sending
- 🧪 **Test Mode**: Safe testing without sending actual emails
- 📱 **Mobile Friendly**: Works on all devices

## 🔧 Troubleshooting

### "Connection Failed"
- ✅ Check your email and password
- ✅ Use app password, not regular password
- ✅ Enable 2-factor authentication

### "CSV Upload Error"
- ✅ Ensure CSV has required columns
- ✅ Check file size (max 10MB)
- ✅ Verify file format (.csv)

### "Port Already in Use"
- ✅ Use different port: `python app.py --port 5002`
- ✅ Kill existing process: `lsof -ti:5001 | xargs kill -9`

## 📞 Support

For issues and questions:
1. Check campaign status for error messages
2. Verify your email configuration
3. Test in test mode first
4. Check the troubleshooting section above

## 🎉 Ready to Get Started?

1. **Install** dependencies: `pip install -r requirements.txt`
2. **Run** the app: `python app.py`
3. **Configure** your email
4. **Upload** your contact list
5. **Start** your first campaign!

**Happy emailing! 📧✨**