import React, {useState, useEffect} from 'react';

function CodeList() {
    const [data_list, setData] = useState([]); 

    useEffect (() => {
        fetch(`/code`).then(
            response => response.json([])
        ).then(data_list=>setData(data_list.list))
    },[]);
    const codeList = data_list;
    console.log("data:", codeList);
    return(
        <div>
            {codeList.map(company=> (<p><a href="`$code/{}`"></a>{company.code} {company.name}</p>))}
        </div>
    );
}

export default CodeList;