const express = require('express');
const axios = require('axios');

const router = express.Router();

router.get('/get_circuits', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_circuits');
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

router.get('/get_drivers', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_drivers');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_event/:year/:event', async (req, res) => {
    const { year, event } = req.params;
    try {
        const response = await axios.get(`http://localhost:8000/api/f1/get_drivers/${year}/${event}`);
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

router.get('/get_next_event', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_next_event');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_previous_champions', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_previous_champions');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_qualifying_results/:year/:round', async (req, res) => {
    const { year, round } = req.params;
    try {
        const response = await axios.get(`http://localhost:8000/api/f1/get_qualifying_results/${year}/${round}`);
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_race_calendar/:year', async (req, res) => {
    const { year } = req.params;
    try {
        const response = await axios.get(`http://localhost:8000/api/f1/get_race_calendar/${year}`);
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_race_results/:year/:round', async (req, res) => {
    const { year, round } = req.params;
    try {
        const response = await axios.get(`http://localhost:8000/api/f1/get_race_results/${year}/${round}`);
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});


router.get('/get_recent_rWinners', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_recent_rWinners');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});


router.get('/get_seasons', async (req, res) => {
    try {
        const response = await axios.get('http://localhost:8000/api/f1/get_seasons');
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

router.get('/get_sprint_results/:year/:round', async (req, res) => {
    const { year, round } = req.params;
    try {
        const response = await axios.get(`http://localhost:8000/api/f1/get_sprint_results/${year}/${round}`);
        res.json(response.data);
    } catch (err) {
        console.error(err);
        res.status(500).json({ error: 'Failed to fetch information from API' });
    }
});

module.exports = router;
