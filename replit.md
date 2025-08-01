# Harmony Hands - Student ERP System

## Overview

Harmony Hands is a bilingual (Marathi/English) Student ERP system designed for educational institutions. The application provides comprehensive form management including admission applications, bonafide certificates, hostel applications, case records, and pratinidhan certificates. It features role-based access control with separate dashboards for students and administrators, file upload capabilities, and complete CRUD operations for all form types.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python) with SQLAlchemy ORM using DeclarativeBase
- **Authentication**: Flask-Login with password hashing via Werkzeug security
- **Database**: SQLite by default, configurable to PostgreSQL or other databases via DATABASE_URL environment variable
- **File Management**: Werkzeug secure filename handling with timestamp-based file naming
- **Session Management**: Flask sessions with configurable secret key
- **Form Processing**: Flask-WTF with CSRF protection and file upload validation
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies

### Frontend Architecture
- **CSS Framework**: Bootstrap 5.3.3 for responsive design
- **Icons**: Font Awesome 6.0.0 for consistent iconography
- **Typography**: Google Fonts Noto Sans Devanagari for Marathi language support
- **JavaScript**: Vanilla JavaScript with Bootstrap components for interactivity
- **Template Engine**: Jinja2 with template inheritance and bilingual content

### Database Design
- **User Model**: Unified user table with role differentiation (is_admin field)
- **Student ID System**: Auto-generated STU001-STU300 format with sequential assignment
- **Form Models**: Separate tables for each form type (AdmissionForm, BonafideForm, HostelForm, CaseRecord, PratinidhanForm)
- **Relationships**: One-to-many relationships between User and all form types
- **Connection Pool**: Configured with pool recycling (300s) and pre-ping for reliability

### Security Architecture
- **Password Security**: Werkzeug password hashing with salt
- **CSRF Protection**: Flask-WTF CSRF tokens on all forms
- **File Upload Security**: Restricted file types with secure filename handling
- **Session Security**: Configurable session secret with environment variable fallback
- **Access Control**: Login required decorators and role-based route protection

### Form Management System
- **Multi-form Support**: Five distinct form types with individual processing workflows
- **File Uploads**: Image and PDF support with size limits (16MB max)
- **Form Validation**: Server-side validation with WTForms validators
- **Form States**: Tracking system for form submission status
- **Bilingual Forms**: Marathi and English field labels and validation messages

## External Dependencies

### Frontend Dependencies
- **Bootstrap 5.3.3**: CSS framework via CDN
- **Font Awesome 6.0.0**: Icon library via CDN  
- **Google Fonts**: Noto Sans Devanagari for Marathi text rendering

### Python Package Dependencies
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering
- **Werkzeug**: WSGI utilities and security functions

### Database
- **SQLite**: Default database (development)
- **PostgreSQL**: Production database option via DATABASE_URL
- **Connection Pooling**: SQLAlchemy engine options for production reliability

### Development Tools
- **Logging**: Python logging module with DEBUG level configuration
- **File System**: OS module for upload directory management
- **Environment Variables**: Support for DATABASE_URL and SESSION_SECRET configuration