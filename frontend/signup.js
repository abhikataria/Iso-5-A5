const signUpButton = document.getElementById('signUp');
  const signInButton = document.getElementById('signIn');
  const container = document.getElementById('container');
  
  signUpButton.addEventListener('click', () => {
    container.classList.add("right-panel-active");
  });
  
  signInButton.addEventListener('click', () => {
    container.classList.remove("right-panel-active");
  });


function valid()
{
  password1 = document.getElementById("ip"); 
  password2 =document.getElementById("nip"); 

  

  // If password not entered 
  //if (password1.value == '') 
    //  alert ("Please enter Password"); 
        
  // If confirm password not entered 
  //else if (password2.value == '') 
    //  alert ("Please enter confirm password"); 
        
  // If Not same return False.     
  //else if (password1.value != password2.value) { 
    //  alert ("\nPassword did not match: Please try again...") 
      //return false; 
  //} 

  // If same return True. 
  //else{ 
    //  alert("WELCOME!") 
      //return true; 
  } 
}
