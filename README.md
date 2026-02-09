# ML Game Prediction System: League of Legends

This project leverages data analytics and machine learning to create a game-winning percentage prediction tool for **League of Legends**. By evaluating historical and real-time data through the Riot Games API, the system provides strategic insights for players, coaches, and analysts.

---

## ## Project Overview
The application is designed to predict outcomes at every stage of a match—pre-game, in-game, and post-game—by analyzing player statistics, champion picks, and team compositions.

### ### Key Features
* **Real-Time Predictions:** Dynamic win probability adjustments during live matches, updating every 20–30 seconds based on objectives, kills, and gold lead.
* **Pre-Game Strategy:** Tools to develop strategies during champion selection and the loading screen.
* **Post-Game Reports:** Detailed performance reviews comparing your stats against rank averages to identify strengths and weaknesses.
* **Data Visualization:** Clear, color-coded visualizations of win chances and contributing factors.
* **Cross-Platform:** A responsive web interface accessible via PC and mobile browsers.

---

## ## Technical Architecture
The system is built using the **Model-View-Controller (MVC)** architecture pattern to ensure a clear separation of concerns between data, logic, and the user interface.



* **Model:** Manages data logic, machine learning algorithms (Linear Regression and Gradient Boosting), and Riot API interactions.
* **View:** The presentation layer responsible for displaying dashboards, charts, and predictions.
* **Controller:** Processes user input and coordinates data flow between the Model and View.
* **Design Pattern:** Utilizes the **Repository Pattern** to abstract data access, allowing the app to switch between the Riot API, local databases, and cached data seamlessly.

---

## ## Tech Stack
* **Machine Learning:** PyTorch.
* **Algorithms:** Linear Regression and Gradient Boosting.
* **Database:** MySQL for application and user-related data.
* **Authentication:** Firebase Authentication.
* **API:** Riot Games API (supports League of Legends, with future scalability for Valorant and TFT).
* **Front-End:** React-based interface with a minimalist UX design.

---

## ## Performance Goals
* **Accuracy:** Target of at least 80% prediction accuracy on validation data.
* **Speed:** Initial predictions and calculations are processed within approximately 1 second.
* **Reliability:** 99% availability during League of Legends server uptime.

---

## ## Group Members
* **Ryan Taheri**
* **Jason Luu**
* **Lukas Lin**

---

## ## License & Constraints
This project is developed as a **CPSC 490 Capstone Project**. All usage must comply with the **Riot Games API Terms of Service**. The system is designed to preserve competitive integrity and does not dictate player actions or access restricted real-time data such as exact gold generation or jungle camp timers.
