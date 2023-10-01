const USER_ID = "EBFDM7iDa4jMcRWl7";
const SERVICE_ID = "service_322jbag";
const TEMPLATE_ID = "template_xdlt3cl";

const ContactFormSubmit = async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const finalForm = Object.fromEntries(formData);
  var data = {
    service_id: SERVICE_ID,
    template_id: TEMPLATE_ID,
    user_id: USER_ID,
    template_params: { ...finalForm },
  };
  var json = JSON.stringify(data);
  const request = await fetch("https://api.emailjs.com/api/v1.0/email/send", {
    method: "POST",
    body: json,
    headers: {
      "Content-Type": "application/json",
    },
  });
  const response = await request.json();
  if (request.ok) {
    console.log("done", response);
  } else {
    console.log(response);
  }
};

const form = document.getElementById("contact-form");
if (form) {
  form.addEventListener("submit", ContactFormSubmit);
}

// turn comment item into html

function formatComment(comment) {
  return `
  <div class="card tw-p-3 tw-max-w-[75%] mb-4">
    <div class="d-flex justify-content-between g-5 tw-mb-3">
        <p class="tw-font-bold">${comment.author}</p>
        <p class="">${comment.time}</p>
    </div>
  
      <p>${comment.comment}</p>
</div> 
  `;
}

// formsetting active class on current url

// Get the current URL
var currentUrl = window.location.href;

// Get all the <li> elements within the <nav> tag
var liElements = document.querySelectorAll("nav li");

// Loop through each <li> element
liElements.forEach(function (liElement) {
  // Get the <a> tag within the current <li> element
  var aTag = liElement.querySelector("a");
  // Check if the <a> tag's href attribute matches the current URL
  if (aTag && aTag.href === currentUrl && aTag.id != "dropdown") {
    // Set the className of the current <li> element to "active"
    aTag.classList.add("active");
  } else if (aTag) {
    aTag.classList.replace("active", "n");
  }
});

function getPage(path) {
  window.location.href = path;
}
