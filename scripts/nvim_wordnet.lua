local json = require('json')
-- Function to get the current word under the cursor and insert a message into the buffer
local function greet_current_word()
  -- Get the current word under the cursor
  local current_word = vim.fn.expand('<cword>')
  
  -- If there is a word, insert the greeting message
  if current_word ~= "" then
    local greeting = "Hello, " .. current_word

    -- Get the current cursor position
    local row, col = unpack(vim.api.nvim_win_get_cursor(0))

    -- Insert the greeting message at the cursor position
    vim.api.nvim_put({greeting}, 'l', true, true)
  else
    print("No word under cursor")
  end
end

-- Create a command to call the function
vim.api.nvim_create_user_command(
  'GreetCurrentWord',
  greet_current_word,
  { nargs = 0 }
)

-- Optionally, you can create a key mapping to call the command
vim.api.nvim_set_keymap(
  'n', 
  '<leader>g', 
  ':GreetCurrentWord<CR>', 
  { noremap = true, silent = true }
)

