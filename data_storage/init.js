db = db.getSiblingDB('logs_db');

// Create necessary collections
db.createCollection('logs');
db.createCollection('predictions');
db.createCollection('drift_metrics');

print("Database 'logs_db' initialized with collections: logs, predictions, drift_metrics");
