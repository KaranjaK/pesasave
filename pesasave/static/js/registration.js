const usernameField = document.querySelector("#usernameField");
const feedBackArea = document.querySelector(".invalid_feedback");
const usernameSuccessOutput = document.querySelector(".usernameSuccessOutput");
const submitBtn = document.querySelector(".submit-btn");

usernameField.addEventListener("keyup", (e) => {
    const usernameVal = e.target.value;
  
    usernameSuccessOutput.style.display = "block";
  
    usernameSuccessOutput.innerHTML = `<i class="bi bi-check2-all"></i> ${usernameVal}`;
    setTimeout((e) =>{
        usernameSuccessOutput.style.display = "none";
    }, 5000)
  
    usernameField.classList.remove("is-invalid");
    feedBackArea.style.display = "none";
    
  
    if (usernameVal.length > 0) {
      fetch("/authentication/validate-username", {
        body: JSON.stringify({ username: usernameVal }),
        method: "POST",
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.username_error) {
            usernameSuccessOutput.style.display = "none";
            usernameField.classList.add("is-invalid");
            feedBackArea.style.display = "block";
            feedBackArea.innerHTML = `<p>${data.username_error}</p>`;
            submitBtn.disabled = true;
          } else {
            submitBtn.removeAttribute("disabled");
          }
        });
    }
  });