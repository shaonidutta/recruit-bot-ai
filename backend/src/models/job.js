const mongoose = require('mongoose');

const jobSchema = new mongoose.Schema({
    title: String,
    company: String,
    url: String,
    // extend fields as necessary
});

module.exports = mongoose.model('Job', jobSchema);
