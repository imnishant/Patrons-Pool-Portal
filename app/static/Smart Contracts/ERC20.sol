pragma solidity ^ 0.5 .0;

library SafeMath
{
  function add (uint256 a, uint256 b) internal pure returns (uint256)
  {
    uint256 c = a + b;
      require (c >= a, "SafeMath: addition overflow");
      return c;
  }

  function sub (uint256 a, uint256 b) internal pure returns (uint256)
  {
    return sub (a, b, "SafeMath: subtraction overflow");
  }

  function sub (uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256)
  {
    require (b <= a, errorMessage);
    uint256 c = a - b;
    return c;
  }

  function mul (uint256 a, uint256 b) internal pure returns (uint256)
  {
    // Gas optimization: this is cheaper than requiring 'a' not being zero, but the
    // benefit is lost if 'b' is also tested.
    if (a == 0){
	    return 0;
    }
    uint256 c = a * b;
    require (c / a == b, "SafeMath: multiplication overflow");
    return c;
  }

  function div (uint256 a, uint256 b) internal pure returns (uint256)
  {
    return div (a, b, "SafeMath: division by zero");
  }

  function div (uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256)
  {
    // Solidity only automatically asserts when dividing by 0
    require (b > 0, errorMessage);
    uint256 c = a / b;
    // assert(a == b * c + a % b); // There is no case in which this doesn't hold
    return c;
  }

  function mod (uint256 a, uint256 b) internal pure returns (uint256) {
    return mod (a, b, "SafeMath: modulo by zero");
  }

  function mod (uint256 a, uint256 b, string memory errorMessage) internal pure returns (uint256)
  {
    require (b != 0, errorMessage);
    return a % b;
  }
}

interface IERC20
{
  function totalSupply () external view returns (uint256);
  function balanceOf (address who) external view returns (uint256);
  function allowance (address owner, address spender)
  external view returns (uint256);
  function transfer (address to, uint256 value) external returns (bool);
  function approve (address spender, uint256 value) external returns (bool);
  function transferFrom (address from, address to, uint256 value)
  external returns (bool);
  event Transfer (address indexed from, address indexed to, uint256 value);
  event Approval (address indexed owner, address indexed spender, uint256 value);
}

contract ERC20 is IERC20
{
  using SafeMath for uint256;
  string private _name;
  string private _symbol;
  uint8 private _decimals;
  uint256 private _totalSupply;
  mapping (address = >uint256)
  private _balances;
  mapping (address = >mapping (address = >uint256)) private _allowed;
  constructor (string memory name, string memory symbol, uint8 decimals, uint256 totalSupply) public {
    _name = name;
    _symbol = symbol;
    _decimals = decimals;
    _totalSupply = totalSupply;
    _balances[0xac7FA16Bdcb3E31904394E4F03c77a9572E1bFfa] = totalSupply;
  }

  /**
   * @return the name of the token.
   */
  function name () public view returns (string memory) {
    return _name;
  }

  /**
   * @return the symbol of the token.
   */
  function symbol () public view returns (string memory) {
    return _symbol;
  }

  /**
   * @return the number of decimals of the token.
   */
  function decimals () public view returns (uint8){
    return _decimals;
  }

  /**
  * @dev Total number of tokens in existence
  */
  function totalSupply () public view returns (uint256) {
    return _totalSupply;
  }
  function balanceOf (address owner) public view returns (uint256){
    return _balances[owner];
  }
  function allowance (address owner, address spender) public view returns (uint256){
    return _allowed[owner][spender];
  }
  function transfer (address to, uint256 value) public returns (bool){
    _transfer (msg.sender, to, value);
    return true;
  }

  function approve (address spender, uint256 value) public returns (bool)
  {
    require (spender != address (0));

    _allowed[msg.sender][spender] = value;
    emit Approval (msg.sender, spender, value);
    return true;
  }

  function transferFrom (address from,
			 address to, uint256 value) public returns (bool)
  {
    require (value <= _allowed[from][msg.sender]);

    _allowed[from][msg.sender] = _allowed[from][msg.sender].sub (value);
    _transfer (from, to, value);
    return true;
  }

  function increaseAllowance (address spender,
			      uint256 addedValue) public returns (bool)
  {
    require (spender != address (0));

    _allowed[msg.sender][spender] =
      (_allowed[msg.sender][spender].add (addedValue));
    emit Approval (msg.sender, spender, _allowed[msg.sender][spender]);
    return true;
  }


  function decreaseAllowance (address spender,uint256 subtractedValue) public returns (bool){
    require (spender != address (0));
    _allowed[msg.sender][spender] =(_allowed[msg.sender][spender].sub (subtractedValue));
    emit Approval (msg.sender, spender, _allowed[msg.sender][spender]);
    return true;
  }

  function _transfer (address from, address to, uint256 value) internal{
    require (value <= _balances[from]);
    require (to != address (0));
    _balances[from] = _balances[from].sub (value);
    _balances[to] = _balances[to].add (value);
    emit Transfer (from, to, value);
  }

  function _mint (address account, uint256 value) internal{
    require (account != address (0));
    _totalSupply = _totalSupply.add (value);
    _balances[account] = _balances[account].add (value);
    emit Transfer (address (0), account, value);
  }

  function _burn (address account, uint256 value) internal{
    require (account != address (0));
    require (value <= _balances[account]);
    _totalSupply = _totalSupply.sub (value);
    _balances[account] = _balances[account].sub (value);
    emit Transfer (account, address (0), value);
  }

  function _burnFrom (address account, uint256 value) internal{
    require (value <= _allowed[account][msg.sender]);
    _allowed[account][msg.sender] = _allowed[account][msg.sender].sub (value);
    _burn (account, value);
  }
}
