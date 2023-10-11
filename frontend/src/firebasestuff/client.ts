import { initializeApp } from "firebase/app";

const firebaseConfig = {
    apiKey: "AIzaSyAoZWbe6X5RmsH9HMDVqxyvXu7eI9kd7sM",
    authDomain: "ieee-ras-rero.firebaseapp.com",
    projectId: "ieee-ras-rero",
    storageBucket: "ieee-ras-rero.appspot.com",
    messagingSenderId: "890405454566",
    appId: "1:890405454566:web:20543f9a4126c28c4eb127",
    measurementId: "G-CFK7QYFHCG"
};

export const app = initializeApp(firebaseConfig);