const express = require('express');
const path = require('path');
const app = express();
const port = 3000;

// app.get('/', (req, res) => res.send('Hello World!'))
// https://expressjs.com/en/starter/static-files.html
console.log(path.join(__dirname, '../site'));
app.use('/', express.static(path.join(__dirname, '../site')));
app.listen(port, () => console.log(`Example app listening on port ${port}!`));
