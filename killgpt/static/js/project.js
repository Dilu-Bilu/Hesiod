/* Project specific Javascript goes here. */

    window.onload = function() {
        document.getElementById("loading-screen").style.display = "none";
    };
    window.onbeforeunload = function() {
        document.getElementById("loading-screen").style.display = "block";
    };
    const menuToggle = document.querySelector('.toggle');
    const showcase = document.querySelector('.showcase');

    menuToggle.addEventListener('click', () => {
      menuToggle.classList.toggle('active');
      showcase.classList.toggle('active');
    })