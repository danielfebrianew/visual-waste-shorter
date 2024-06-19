import express from "express";
import {addWaste, getAllWastes, getWaste} from "../controllers/WasteController.js"

const router = express.Router();

router.get('/waste', getAllWastes);
router.get('/waste/:id', getWaste);
router.post('/waste', addWaste);

export default router;