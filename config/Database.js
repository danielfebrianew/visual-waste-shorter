import {Sequelize} from "sequelize";

const db = new Sequelize('waste_db', 'root', '', {
    host: "localhost",
    dialect: "mysql"
});

export default db;