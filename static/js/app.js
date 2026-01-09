//register user
async function userRegister() {
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password1 = document.getElementById("password").value;
    const password2 = document.getElementById("confirm_password").value;
    const button = document.getElementById("submitButton");

    if (!username || !email || !password1 || !password2) {
        alert("Please complete all required fields.");
        return;
    }

    if (password1 !== password2) {
        alert("Passwords do not match. Please try again.");
        return;
    }

    try {
        button.disabled = true;
        const response = await fetch("/user/register/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password1
            })
        });

        const data = await response.json();

        if (!response.ok) {
            if (response.status === 403) {
                alert("An account with this username or email already exists.");
            } else {
                alert(data.detail || "A server error occurred. Please try again later.");
            }
            return;
        }

        alert("Registration successful! Redirecting to login...");
        window.location.href = "/login";

    } catch (error) {
        console.error("Registration Error:", error);
        alert("Unable to connect to the server. Please check your internet connection.");
    } finally {
        if (button) button.disabled = false;
    }
}

async function userLogin(){

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;;
    const button = document.getElementById("submitButton");

    if (!username || !password) {
        alert("Please enter both your username and password.");
        return;
    }

    try{
        const formData = new URLSearchParams();
        formData.append("username", username);
        formData.append("password", password);
        button.disabled = true;
        const response = await fetch("/user/login/", {
            method: "POST",
             headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Invalid username or password.");
            return;
        }

        localStorage.setItem("token", data.access_token);
        window.location.href = "/submit-code";

    } catch (error) {
        console.error("Login Error: ", error);
        alert("Unable to connect to the server. Please check your internet connection.");
    } finally {
        button.disabled = false;
    }
}


//submit the code
async function submitCode() {

    const codeText = document.getElementById("codeInput").value;
    const responseBox = document.getElementById("resultBox");
    const button = document.getElementById("submitButton");
    const token = localStorage.getItem("token");

    const summary = document.getElementById("summaryCode");
    const logic_list = document.getElementById("logicList");
    const issues_list = document.getElementById("issuesList");
    const improvement_list = document.getElementById("improvementsList");
    const time_span = document.getElementById("timeDisplay");
    const space_span = document.getElementById("spaceDisplay");
    const space_expl = document.getElementById("spaceExplanation");
    const time_expl = document.getElementById("timeExplanation");

    if (!codeText) {
        responseBox.innerText = "Please enter some code.";
        return;
    }

    if (!token) {
        alert("No token found, redirecting...");
        window.location.href = "/login";
        return;
    }

    try {

        summary.innerHTML = "";
        logic_list.innerHTML = "";
        issues_list.innerHTML = "";
        improvement_list.innerHTML = "";


        button.disabled = true;
        responseBox.innerText = "Analyzing code... please wait.";

        const response = await fetch("/submit-code/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                code_text: codeText
            })
        });

        const data = await response.json();

        if (!response.ok) {
            if (response.status === 401) {
                alert("Session expired.");
                localStorage.removeItem("token");
                window.location.href = "/login";
                return;
            }
            responseBox.innerText = `Server error: ${data.detail || "Unknown error"}`;
            return;
        }

        responseBox.style.display = "none"; 
        document.getElementById("analysisResult").style.display = "block";

        const ai_response = data.ai_response;
        summary.innerText = ai_response.summary;
        
        ai_response.logic_breakdown.forEach(logic => {
            const li = document.createElement("li");
            li.className = "list-group-item list-group-item-light py-1 small";
            li.innerText = logic;
            logic_list.appendChild(li);
        });
        
        ai_response.potential_issues.forEach(issue => {
            const li = document.createElement("li");
            li.className = "list-group-item list-group-item-danger py-1 small";
            li.innerText = issue;
            issues_list.appendChild(li);
        });

        ai_response.improvements.forEach(improvement => {
            const li = document.createElement("li");
            li.className = "list-group-item list-group-item-success py-1 small";
            li.innerText = improvement;
            improvement_list.appendChild(li);
        });
        time_span.innerText = ai_response.time_complexity.notation;
        time_expl.innerText = ai_response.time_complexity.explanation;
        space_span.innerText = ai_response.space_complexity.notation;
        space_expl.innerText = ai_response.space_complexity.explanation;
    
    } catch (error) {
        console.error("JS Error:", error);
        responseBox.innerText = "Connection failed";
    } finally {
        button.disabled = false;
    }
}

async function showHistory() {
    const container = document.getElementById("containerHistory");
    const token = localStorage.getItem("token");

    if (!token){
        alert("No token found, redirecting...");
        window.location.href="/login";
        return;
    }

    try{
        const response = await fetch("/api/history/", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (!response.ok){
            if (response.status === 401) {
                alert("Session expired.");
                localStorage.removeItem("token");
                window.location.href = "/login";
                return;
            }
            return;
        }

        const data = await response.json();
        if (data.length == 0){
            container.innerHTML = '<p class="text-centre">No History found</p>';
            return;
        }

        let htmlContent = '<div class="row row-cols-1 row-cols-md-3 g-4">';

        for (let code of data) {

            const date = new Date(code.created_at).toLocaleDateString();

            const preview = code.code_text.length > 100 ? code.code_text.substring(0, 100) + "..." : code.code_text;

            htmlContent += `
                <div class="col" id="card-${code.id}">
                    <div class="card h-100 shadow-sm">
                        <div class="card-body d-flex flex-column">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h5 class="card-title">${code.ai_result.heading}</h5>
                                <button class="btn btn-link text-dark p-0" onclick="deleteChat(${code.id})">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                            <p class="card-text text-muted small">${date}</p>
                            <pre class="card-text small bg-light p-2" style="max-height: 100px; overflow: hidden;">${preview}</pre>
                            <a href="/history/${code.id}/" class="btn btn-primary btn-sm mt-auto">View Details</a>
                        </div>
                    </div>
                </div>`;
        }
        htmlContent += '</div>';

        container.innerHTML = htmlContent;

    } catch (error) {
        console.error("JS error: ", error);
    }
}


async function deleteChat(id){
    const token = localStorage.getItem("token");
    try{
        const response = await fetch(`/history/${id}/`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            },
        });
        if (!response.ok){
            if (response.status === 401) {
                alert("Session expired.");
                localStorage.removeItem("token");
                window.location.href = "/login";
                return;
            }
            return;
        }
        const card = document.getElementById(`card-${id}`);
        card.remove();
    } catch (error) {
        console.error("JS Error: ", error);
    }
}


async function showSingleChat(id){
    const title = document.getElementById("analysisTitle");
    const date = document.getElementById("analysisDate");
    const user_code = document.getElementById("viewCode");
    const summary = document.getElementById("summaryCode");
    const logic_list = document.getElementById("logicList");
    const issues_list = document.getElementById("issuesList");
    const improvement_list = document.getElementById("improvementsList");
    const time_span = document.getElementById("timeDisplay");
    const space_span = document.getElementById("spaceDisplay");
    const space_expl = document.getElementById("spaceExplanation");
    const time_expl = document.getElementById("timeExplanation");


    const token = localStorage.getItem("token");

    if (!token){
        alert("No token found, redirecting...");
        window.location.href = "/login";
        return;
    }
    try{
        const response = await fetch(`/api/history/${id}/`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (!response.ok){
            if (response.status === 401) {
                alert("Session expired.");
                localStorage.removeItem("token");
                window.location.href = "/login";
                return;
            }
            return;
        }
        
        const data = await response.json();
        title.innerText = data.ai_result.heading;
        const date_var = new Date(data.created_at).toLocaleDateString();
        date.innerText = date_var;
        user_code.innerText = data.code_text; 
        document.getElementById("analysisResult").style.display = "block";

        const ai_response = data.ai_result;
        summary.innerText = ai_response.summary;
        
        ai_response.logic_breakdown.forEach(logic => {
            const li = document.createElement("li");
            li.className = "list-group-item list-group-item-light py-1 small";
            li.innerText = logic;
            logic_list.appendChild(li);
        });
        
        ai_response.potential_issues.forEach(issue => {
            const li = document.createElement("li");
            li.className = "list-group-item list-group-item-danger py-1 small";
            li.innerText = issue;
            issues_list.appendChild(li);
        });

        ai_response.improvements.forEach(improvement => {
            const li = document.createElement("li");
            li.className = "list-group-item list-group-item-success py-1 small";
            li.innerText = improvement;
            improvement_list.appendChild(li);
        });
        time_span.innerText = ai_response.time_complexity.notation;
        time_expl.innerText = ai_response.time_complexity.explanation;
        space_span.innerText = ai_response.space_complexity.notation;
        space_expl.innerText = ai_response.space_complexity.explanation;

    } catch (error) {
        console.error("JS Error: ", error);
    }

}

async function searchHistory(){

    const search_key = document.getElementById("historySearch").value;
    const button = document.getElementById("searchButton");
    const container = document.getElementById("containerHistory");
    const token = localStorage.getItem("token");

    try{
        button.disabled = true;
        const response = await fetch(`/search?q=${encodeURIComponent(search_key)}`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        const data = await response.json();

        if (data.length == 0){
            container.innerHTML = `<p class="text-centre">No matches found for ${search_key}</p>`;
            return;
        }

        let htmlContent = '<div class="row row-cols-1 row-cols-md-3 g-4">';

        for (let code of data) {

            const date = new Date(code.created_at).toLocaleDateString();

            const preview = code.code_text.length > 100 ? code.code_text.substring(0, 100) + "..." : code.code_text;

            htmlContent += `
                <div class="col" id="card-${code.id}">
                    <div class="card h-100 shadow-sm">
                        <div class="card-body d-flex flex-column">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h5 class="card-title">${code.ai_result.heading}</h5>
                                <button class="btn btn-link text-dark p-0" onclick="deleteChat(${code.id})">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                            <p class="card-text text-muted small">${date}</p>
                            <pre class="card-text small bg-light p-2" style="max-height: 100px; overflow: hidden;">${preview}</pre>
                            <a href="/history/${code.id}/" class="btn btn-primary btn-sm mt-auto">View Details</a>
                        </div>
                    </div>
                </div>`;
        }
        htmlContent += '</div>';

        container.innerHTML = htmlContent;
        
    } catch (error) {
        console.error("JS Error: ", error);
    } finally {
        button.disabled = false;
    }
}

function logout(){
    localStorage.removeItem("token");
    window.location.href = "/login";
}