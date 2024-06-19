import { Sequelize } from "sequelize";
import db from "../config/Database.js";
import Waste from "./WasteModel.js"; // Import your Waste model

const { DataTypes } = Sequelize;

const Prediction = db.define('predictions', {
    id: {
        type: DataTypes.INTEGER,
        autoIncrement: true,
        primaryKey: true
    },
    waste_id: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: Waste, // This is the Waste model
            key: 'id'
        },
        validate: {
            notEmpty: true
        }
    },
    confidence: {
        type: DataTypes.FLOAT,
        allowNull: false,
        validate: {
            notEmpty: true
        }
    }
}, {
    freezeTableName: true
});

// Set up the associations
Waste.hasMany(Prediction, { foreignKey: 'waste_id' });
Prediction.belongsTo(Waste, { foreignKey: 'waste_id' });

export default Prediction;

// (async () => { 
//     try {
//         await db.sync();
//         console.log("Database synchronized");
//     } catch (error) {
//         console.error("Error synchronizing database:", error);
//     }
// })();
