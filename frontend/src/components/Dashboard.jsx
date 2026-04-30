import { useState } from "react";
import DatasetView from "./DatasetView";
import Simulator from "./Simulator";

function Dashboard() {
  const [simulatedData, setSimulatedData] = useState([]);

  return (
    <div className="container">

      {/* HEADER */}
      <div className="header">
        <h1 style={{"font-size":"40px"}}>Serverless Cold Start Optimization</h1>
        <p style={{"font-size":"20px"}}>Predict workload, prewarm containers, reduce latency</p>
      </div>

      {/* DATASET */}
      <div className="dataset">
        <DatasetView simulated={simulatedData} />
      </div>

      {/* SIMULATOR */}
      <Simulator setSimulatedData={setSimulatedData} />

    </div>
  );
}

export default Dashboard;