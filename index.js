import express from "express";
import cors from "cors";
import session from "express-session";
import dotenv from "dotenv";
import db from "./config/Database.js";
import SequelizeStore from "connect-session-sequelize";
import UserRoute from "./routes/UserRoute.js";
import ProductRoute from "./routes/ProductRoute.js";
import AuthRoute from "./routes/AuthRoute.js";
// import bodyParser from './body-parser';
import axios from 'axios';
import Prediction from "./models/PredictionModel.js";
import WasteRoute from "./routes/WasteRoute.js";
dotenv.config();

const app = express();

const sessionStore = SequelizeStore(session.Store);

const store = new sessionStore({
    db: db
});

(async()=>{
    await db.sync();
})();

app.use(session({
    secret: process.env.SESS_SECRET,
    resave: false,
    saveUninitialized: true,
    store: store,
    cookie: {
        secure: 'auto'
    }
}));

app.use(cors({
    credentials: true,
    origin: 'http://localhost:3000'
}));
app.use(express.json());
// app.use(bodyParser.json());
app.use(UserRoute);
app.use(ProductRoute);
app.use(AuthRoute);
app.use(Prediction);
app.use(WasteRoute);

app.post('/predict', async (req, res) => {
    try {
        const response = await axios.post('http://localhost:3000/predict', req.body);
        res.send(response.data);
    } catch (error) {
        res.status(500).send(error.toString());
    }
});

store.sync();

app.listen(process.env.APP_PORT, ()=> {
    console.log('Server up and running...');
});
