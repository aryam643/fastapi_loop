# Store Monitoring System

A comprehensive backend API system for monitoring restaurant store uptime and generating detailed reports. Built with FastAPI, SQLAlchemy, and advanced business hours logic.

## System Architecture
<img width="3771" height="3840" alt="system_flow" src="https://github.com/user-attachments/assets/f0469a4f-46a1-4557-ba09-f37fda7b2dba" />


## Data Flow Diagram

<img width="1302" height="209" alt="data_flow" src="https://github.com/user-attachments/assets/4bfe5208-1881-4e60-83d5-a16daea5e5a7" />

## API Sequences

<img width="704" height="593" alt="api_sequence" src="https://github.com/user-attachments/assets/f32bec5d-d4c1-49d9-8d9d-92c88885ac82" />

## Features

- **Async Report Generation**: Trigger reports and poll for completion
- **Business Hours Support**: Handles complex business hours including overnight operations
- **Timezone Conversion**: Robust timezone handling with DST support
- **Data Interpolation**: Smart extrapolation from sparse polling data
- **CSV Export**: Validated CSV reports with statistics and formatting
- **RESTful API**: Clean FastAPI endpoints with proper error handling

## Project Structure

\`\`\`
store-monitoring/
├── main.py                    # FastAPI application with endpoints
├── models.py                  # SQLAlchemy database models
├── database.py                # Database configuration and session management
├── data_processor.py          # Data import and processing logic
├── report_generator.py        # Core report generation engine
├── report_service.py          # Service layer for report management
├── business_hours_utils.py    # Enhanced business hours calculations
├── csv_export_utils.py        # CSV export and validation utilities
├── data_import_script.py      # Script to import CSV data
├── run_server.py              # Server startup script
├── test_api.py                # API testing script
├── test_business_hours.py     # Business hours logic tests
├── generate_sample_report.py  # Sample report generation
├── requirements.txt           # Python dependencies
├── start_server.sh            # Server startup script
├── data/                      # Directory for CSV input files
└── reports/                   # Directory for generated CSV reports
\`\`\`

## API Endpoints

### 1. Trigger Report Generation
\`\`\`
POST /trigger_report
\`\`\`
**Response:**
\`\`\`json
{
  "report_id": "uuid-string"
}
\`\`\`

### 2. Get Report Status/Download
\`\`\`
GET /get_report/{report_id}
\`\`\`
**Responses:**
- If running: `{"status": "Running", "created_at": "timestamp"}`
- If complete: Downloads CSV file with schema:
  \`\`\`
  store_id,uptime_last_hour,uptime_last_day,uptime_last_week,downtime_last_hour,downtime_last_day,downtime_last_week
  \`\`\`

### 3. Health Check
\`\`\`
GET /health
\`\`\`

## Setup Instructions

### 1. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. Prepare Data
Place your CSV files in the `data/` directory:
- `store_status.csv` - Store polling data
- `business_hours.csv` - Business hours data  
- `store_timezones.csv` - Timezone data

### 3. Import Data
\`\`\`bash
python data_import_script.py
\`\`\`

### 4. Start Server
\`\`\`bash
python run_server.py
# OR
chmod +x start_server.sh
./start_server.sh
\`\`\`

The API will be available at `http://localhost:8000`

## Testing

### Test API Endpoints
\`\`\`bash
python test_api.py
\`\`\`

### Test Business Hours Logic
\`\`\`bash
python test_business_hours.py
\`\`\`

### Generate Sample Reports
\`\`\`bash
python generate_sample_report.py
\`\`\`

## Key Features Explained

### Business Hours Logic
- Supports normal hours (9 AM - 5 PM) and overnight hours (10 PM - 6 AM)
- Handles timezone conversions with DST support
- Defaults to 24/7 operation if no business hours defined
- Defaults to America/Chicago timezone if not specified

### Report Generation Algorithm
1. **Data Collection**: Retrieves store status data for last hour/day/week
2. **Timezone Conversion**: Converts UTC timestamps to local store time
3. **Business Hours Filtering**: Only considers data within business hours
4. **Interpolation**: Extrapolates uptime/downtime from sparse polling data
5. **Aggregation**: Calculates total uptime/downtime for each period
6. **Export**: Generates validated CSV with proper formatting

### Data Interpolation Logic
- For consecutive observations, assumes status remains constant between them
- Handles edge cases at period boundaries
- Only counts time within business hours
- Provides fallback values for stores with no data

## Performance Considerations

- **Async Processing**: Report generation runs in background threads
- **Batch Operations**: Efficient database queries and bulk inserts
- **Memory Management**: Processes stores in batches to handle large datasets
- **File Management**: Automatic cleanup of old report files

## Error Handling

- Comprehensive logging throughout the system
- Graceful degradation for missing data
- Validation of CSV data and business hours
- Proper HTTP status codes and error messages

## Sample Output

The system generates CSV reports with the following schema:
\`\`\`csv
store_id,uptime_last_hour,uptime_last_day,uptime_last_week,downtime_last_hour,downtime_last_day,downtime_last_week
store_0001,58.50,22.75,165.25,1.50,1.25,2.75
store_0002,45.25,18.50,142.00,14.75,5.50,26.00
\`\`\`

## Improvements for Production

### 1. **Database & Performance**
- **PostgreSQL Migration**: Replace SQLite with PostgreSQL for better concurrency and performance
- **Database Indexing**: Add composite indexes on (store_id, timestamp_utc) for faster queries
- **Connection Pooling**: Implement connection pooling with SQLAlchemy for better resource management
- **Query Optimization**: Use database-specific optimizations and query hints
- **Partitioning**: Partition large tables by date for better query performance

### 2. **Caching & Memory Management**
- **Redis Integration**: Cache frequently accessed store metadata and business hours
- **Query Result Caching**: Cache report calculations for common time periods
- **Memory-Efficient Processing**: Stream large datasets instead of loading everything into memory
- **Background Cache Warming**: Pre-calculate common reports during off-peak hours

### 3. **Scalability & Architecture**
- **Microservices**: Split into separate services (data ingestion, report generation, API)
- **Message Queues**: Use Celery with Redis/RabbitMQ for distributed task processing
- **Load Balancing**: Implement horizontal scaling with multiple API instances
- **Container Orchestration**: Deploy with Kubernetes for auto-scaling and resilience
- **CDN Integration**: Serve generated reports through CDN for faster downloads

### 4. **Monitoring & Observability**
- **Metrics Collection**: Implement Prometheus metrics for API performance and system health
- **Distributed Tracing**: Add OpenTelemetry for request tracing across services
- **Structured Logging**: Use structured JSON logging with correlation IDs
- **Health Checks**: Advanced health checks including database connectivity and disk space
- **Alerting**: Set up alerts for failed report generations and system anomalies

### 5. **Security & Compliance**
- **Authentication**: Implement JWT-based authentication with role-based access control
- **API Rate Limiting**: Add rate limiting per user/API key to prevent abuse
- **Data Encryption**: Encrypt sensitive data at rest and in transit
- **Audit Logging**: Track all data access and modifications for compliance
- **Input Validation**: Enhanced validation and sanitization of all inputs

### 6. **Data Management & Quality**
- **Data Pipeline**: Implement ETL pipelines for automated data ingestion and validation
- **Data Quality Checks**: Add data quality monitoring and anomaly detection
- **Backup Strategy**: Automated backups with point-in-time recovery
- **Data Retention**: Implement data lifecycle management and archiving
- **Schema Evolution**: Version control for database schema changes

### 7. **Advanced Features**
- **Real-time Updates**: WebSocket support for real-time report status updates
- **Report Scheduling**: Allow users to schedule recurring reports
- **Custom Time Ranges**: Support for arbitrary date ranges in reports
- **Data Visualization**: Add charts and graphs to reports
- **Export Formats**: Support multiple export formats (JSON, Excel, PDF)
- **Notification System**: Email/SMS notifications when reports are ready

### 8. **Development & Operations**
- **CI/CD Pipeline**: Automated testing, building, and deployment
- **Environment Management**: Separate dev/staging/prod environments with infrastructure as code
- **Feature Flags**: Implement feature toggles for safe deployments
- **API Versioning**: Version the API for backward compatibility
- **Documentation**: Auto-generated API documentation with OpenAPI/Swagger

### 9. **Cost Optimization**
- **Resource Monitoring**: Track and optimize compute and storage costs
- **Auto-scaling**: Scale resources based on demand patterns
- **Data Compression**: Compress stored data and reports to reduce storage costs
- **Efficient Algorithms**: Optimize algorithms for better time/space complexity
- **Spot Instances**: Use cloud spot instances for non-critical batch processing

### 10. **Business Intelligence**
- **Analytics Dashboard**: Real-time dashboard showing system usage and store performance trends
- **Predictive Analytics**: ML models to predict store downtime patterns
- **Anomaly Detection**: Automated detection of unusual store behavior patterns
- **Business Metrics**: Track business KPIs like average uptime across regions
- **Custom Reports**: Allow users to create custom report templates

This system provides a robust foundation for store monitoring with room for future enhancements and production deployment.
