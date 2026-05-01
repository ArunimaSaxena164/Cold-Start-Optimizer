import { useState } from "react";
import DatasetView from "./DatasetView";
import Simulator from "./Simulator";
import Explanation from "./Explanation";
function Dashboard() {
  const [simulatedData, setSimulatedData] = useState([]);

  return (
    <div className="container">

      {/* HEADER */}
      <div className="header">
        <h1 style={{"font-size":"50px"}}>Serverless Cold Start Optimization</h1>
        <p>Predict workload, prewarm containers, reduce latency</p>
      </div>

      {/* DATASET */}
      <div className="dataset">
        <DatasetView simulated={simulatedData} />
      </div>

      {/* SIMULATOR */}
      <Simulator setSimulatedData={setSimulatedData} />
 {/* EXPLANATION */}
      <Explanation />
    </div>
  );
}

export default Dashboard;