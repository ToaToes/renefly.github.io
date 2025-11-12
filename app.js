const auth = firebase.auth();

const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const loginBtn = document.getElementById("loginBtn");
const signupBtn = document.getElementById("signupBtn");
const errorMsg = document.getElementById("errorMsg");

// Login
loginBtn.addEventListener("click", () => {
  const email = emailInput.value;
  const password = passwordInput.value;

  auth.signInWithEmailAndPassword(email, password)
    .then((userCredential) => {
        const user = userCredential.user;

        if (user.emailVerified) {
        // Email is verified — go to home.html
        window.location.href = "home.html";
        } else {
        alert("Please verify your email before logging in.");
        auth.signOut(); // Optional: sign out unverified user
        }
    })
    .catch(err => {
      errorMsg.textContent = err.message;
    });
});

// Sign Up
signupBtn.addEventListener("click", () => {
  const email = emailInput.value;
  const password = passwordInput.value;

  /* Sign up the user 
  auth.createUserWithEmailAndPassword(email, password)
    .then(() => {
      window.location.href = "home.html";
    })
    .catch(err => {
      errorMsg.textContent = err.message;
    });
    */
  auth.createUserWithEmailAndPassword(email, password)
    .then((userCredential) => {
        const user = userCredential.user;

        // Send email verification
        user.sendEmailVerification()
        .then(() => {
            alert('Verification email sent! Please check your Inbox, Spam or Junk.');
            // Optionally, redirect to login page or show message
            // 
            // window.location.href = "verify.html";
        });
    })
    .catch(err => {
      errorMsg.textContent = err.message;
    });

});
