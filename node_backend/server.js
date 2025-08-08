const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const axios = require('axios');
const Joi = require('joi');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json({ limit: '10mb' }));

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Validation schemas
const timeWindowSchema = Joi.object({
    start: Joi.string().pattern(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/).required(),
    end: Joi.string().pattern(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/).required()
});

const pickupSchema = Joi.object({
    address: Joi.string().required(),
    zipcode: Joi.string().required(),
    lat: Joi.number().min(-90).max(90).required(),
    lng: Joi.number().min(-180).max(180).required(),
    start_time: Joi.string().pattern(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/).required(),
    end_time: Joi.string().pattern(/^([01]?[0-9]|2[0-3]):[0-5][0-9]$/).required()
});

const settingsSchema = Joi.object({
    return_to_origin: Joi.boolean().default(true),
    time_per_stop_minutes: Joi.number().integer().min(1).max(120).default(10),
    vehicle_speed_kmph: Joi.number().positive().max(200).default(40),
    optimize_by: Joi.string().valid('distance', 'time', 'priority').default('priority')
});

const deliverySchema = Joi.object({
    address: Joi.string().required(),
    zipcode: Joi.string().required(),
    lat: Joi.number().min(-90).max(90).required(),
    lng: Joi.number().min(-180).max(180).required(),
    priority: Joi.number().integer().min(1).max(3).required(),
    time_window: timeWindowSchema.required()
});

const routingRequestSchema = Joi.object({
    pickup: pickupSchema.required(),
    settings: settingsSchema.required(),
    deliveries: Joi.array().items(deliverySchema).min(1).required()
});

// Routes
app.get('/', (req, res) => {
    res.json({
        message: 'Delivery Route Optimization Node.js Backend',
        version: '1.0.0',
        endpoints: {
            optimize_route: '/api/optimize-route',
            health: '/api/health',
            example_data: '/api/example-data'
        }
    });
});

app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'delivery-routing-node-backend',
        python_service: `${PYTHON_API_URL}/health`
    });
});

app.post('/api/optimize-route', async (req, res) => {
    try {
        // Validate request
        const { error, value } = routingRequestSchema.validate(req.body);
        if (error) {
            return res.status(400).json({
                error: 'Validation failed',
                details: error.details
            });
        }

        // Forward request to Python microservice
        const response = await axios.post(`${PYTHON_API_URL}/optimize-route`, value, {
            timeout: 30000, // 30 seconds timeout
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Return the response from Python service
        res.json(response.data);

    } catch (error) {
        console.error('Route optimization error:', error.message);
        
        if (error.code === 'ECONNREFUSED') {
            return res.status(503).json({
                error: 'Python microservice is not available',
                message: 'Please ensure the Python backend is running on the specified URL'
            });
        }
        
        if (error.response) {
            // Python service returned an error
            return res.status(error.response.status).json(error.response.data);
        }
        
        res.status(500).json({
            error: 'Internal server error',
            message: error.message
        });
    }
});

app.get('/api/example-data', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_API_URL}/example-data`);
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching example data:', error.message);
        res.status(500).json({
            error: 'Failed to fetch example data',
            message: error.message
        });
    }
});

app.get('/api/config', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_API_URL}/config`);
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching config:', error.message);
        res.status(500).json({
            error: 'Failed to fetch configuration',
            message: error.message
        });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        error: 'Something went wrong!',
        message: err.message
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Endpoint not found',
        message: `The endpoint ${req.method} ${req.path} does not exist`
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`Node.js backend server running on port ${PORT}`);
    console.log(`Python API URL: ${PYTHON_API_URL}`);
    console.log(`Health check: http://localhost:${PORT}/api/health`);
});

module.exports = app; 