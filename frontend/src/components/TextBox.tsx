import React,{ useState,ChangeEvent } from "react";

interface SearchResponse{
    keyword:string;
    articles:{
        title:string;
        summary:string;
        url:string;
        source:string;
    }[];
}

interface TextBoxProps{
    debounce?:number;
    onResults?: (response:SearchResponse) => void;
}

export default function TextBox({
    debounce = 500,
    onResults,
}: TextBoxProps){
    const [keyword,setKeyword] = useState("");
    const [timerId,settimerId] = useState<NodeJS.Timeout | null>(null);

    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        const newValue = e.target.value;
        setKeyword(newValue)
    
    if(timerId){
        clearTimeout(timerId);
    }
    const newTimerId = setTimeout(() => {
        if(newValue.trim()){
            callBackendAPI(newValue.trim())
        }

    },debounce);
    settimerId(newTimerId)
    }

    async function callBackendAPI(inputKeyword:string){
        try{
            const response = await fetch(`http://localhost:8000/api/search`,{
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({keyword:inputKeyword})
            })
            if(!response.ok){
                console.error("Backend returned an error",response.statusText);
                return;
            }

            const data = (await response.json()) as SearchResponse;
            console.info("Received data from the backend",data);
            if(onResults){
                onResults(data)
            }
        }catch(err){
            console.error("Error calling the backend",err)
        }
    }
    return(
        <input
        type="text"
        value={keyword}
        onChange = {handleChange}
        placeholder="Type a keyword you want to search for"
        style={{width:"300px", fontSize:"1rem"}}
        />
    );

}