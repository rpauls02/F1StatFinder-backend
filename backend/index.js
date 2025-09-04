const express = require('express');
const cors = require('cors');
const routes = require('./routes/f1');

const app = express();
app.use(cors());

app.use('/api/f1', routes);


app.listen(5000, () => {
  console.log('Node backend running on http://localhost:5000');
});