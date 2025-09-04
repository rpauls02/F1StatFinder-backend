const express = require('express');
const axios = require('axios');

const router = express.Router();

router.get('/get_race_calendar', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_race_calendar');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_driver_standings', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_driver_standings');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_driver_stats', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_driver_stats');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_constructor_standings', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_constructor_standings');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_constructor_stats', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_constructor_stats');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_champions', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_champions');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_next_event', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_next_event');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_next_event_countdown', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_next_event_countdown');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_drivers', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_drivers');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_driver_points/:year', async (req, res) => {
    const { year } = req.params;
    try {
        const response = await axios.get(`http://localhost:8000/api/f1/get_driver_points/${year}`);
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_constructor_points/:year', async (req, res) => {
    const { year } = req.params;
    try {
        const response = await axios.get(`http://localhost:8000/api/f1/get_constructor_points/${year}`);
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

module.exports = router;
