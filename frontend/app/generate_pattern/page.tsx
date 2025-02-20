"use client"
import { useRouter } from "next/navigation";
import { useState } from "react";

interface RadioOption {
  value: string;
  label: string;
}

const radioOptions: RadioOption[] = [
  { value: 'fine', label: 'Fine Yarn (fingering, sock, lace etc.)' },
  { value: 'light', label: 'Light (Sport, DK, baby)' },
  { value: 'medium', label: 'Medium (worsted, aran etc.)' },
  { value: 'bulky', label: 'Bulky' },
  { value: 'super_bulky', label: 'Super Bulky' },
];

const craftOptions: RadioOption[] = [
  {value: 'knit', label: "Knit"},
  {value: 'crochet', label: "Crochet"}
]

export default function KnittingForm() {
  const [craftType, setCraftType] = useState<string | undefined>(undefined);
  const [knitItem, setKnitItem] = useState("");
  const [attributes, setAttributes] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedYarnWeight, setSelectedYarnWeight] = useState<string | undefined>(undefined);
  
  const router = useRouter()
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResponse("");

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          "craft_type": craftType,
          "clothing_category": knitItem, 
          "pattern_attributes": attributes,
        "yarn_weight": selectedYarnWeight }),
      });
      
      const sessionId = await response.json()
      console.log("sessionId: ", sessionId)
      //TODO: write a redirect function here
      router.push(`/chat/${sessionId}`)

    } catch (error) {
      console.error("Error:", error);
      setResponse("Error fetching response.");
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="max-w-lg mx-auto p-6 bg-white shadow-lg rounded-xl mt-10">
      <h1 className="text-xl font-bold mb-4">Knitting Assistant</h1>
      <form onSubmit={handleSubmit} className="space-y-4">

        What craft type are you thinking about?
        {
          craftOptions.map((option) => (
            <div key={option.value}>
              <input 
                type="radio"
                id={option.value}
                name="craftRadioGroup"
                value={option.value}
                checked= {craftType === option.value}
                onChange={(e)=> setCraftType(e.target.value)}
              />
              <label className="text-sm"> {option.label}</label>
            </div>
          ))
        }
        What are you trying to make?
        <input
          type="text"
          className="w-full p-2 border rounded-lg"
          placeholder="sweaters, scarf, etc..."
          value={knitItem}
          onChange={(e) => setKnitItem(e.target.value)}
          required
        />

        Input Attributes, comma-separated
        <input
            type="text"
            className="w-full p-2 border rounded-lg"
            placeholder="separate attributes by comma e.g raglan sleeves, round neck... "
            value={attributes}
            onChange={(e) => setAttributes(e.target.value)}
            />
        
        Select Yarn Weight
        {radioOptions.map((option) => (

            <div key={option.value}>
              <input 
                type="radio" 
                id={option.value} 
                name="radioGroup" 
                value={option.value} 
                checked={selectedYarnWeight === option.value} 
                onChange={(e) => setSelectedYarnWeight(e.target.value)} 
              />
              <label className="text-sm" htmlFor={option.value}> {option.label}</label>
            </div>

            ))}
        <button
          type="submit"
          className="w-full bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? "Generating..." : "Get Pattern Help"}
        </button>
      </form>

      {response && (
        <div className="mt-4 p-4 bg-gray-100 rounded-lg">
          <h2 className="text-lg font-semibold">Response:</h2>
          <p className="mt-2">{response}</p>
        </div>
      )}
    </div>
  );
}
