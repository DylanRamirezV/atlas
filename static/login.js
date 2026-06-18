(function(){
  const form = document.getElementById('login-form');
  if(!form) return;

  form.addEventListener('submit', function(e){
    const codeInput = document.getElementById('code');
    const roleInput = document.getElementById('role');
    if(!codeInput || !roleInput) return;

    const code = codeInput.value.trim();
    const role = roleInput.value;

    if(code.length === 9 && /^\d{9}$/.test(code) && ['student','professor','admin'].includes(role)) {
      localStorage.setItem('atlasUserCode', code);
      localStorage.setItem('atlasUserRole', role);
    }
  });
})();
