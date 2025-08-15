const express = require('express');
const router = express.Router();

// Home page route
router.get('/', (req, res) => {
    res.send('Welcome to the Backend Home Page!');
});

module.exports = router;
