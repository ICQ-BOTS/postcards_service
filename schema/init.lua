box.cfg {
    listen = 3321
}

box.schema.user.grant('guest', 'read,write,execute', 'universe', nil, {if_not_exists=true})
box.schema.user.passwd('pass')


function init()

--------------------------------Nouns--------------------------------

if box.space.nouns == nil then
	local nouns = box.schema.space.create('nouns', { if_not_exists = true })
	
	nouns:format({
		{ name = 'id', 				type = 'unsigned' 	},	--0
		{ name = 'noun_word', 		type = 'string' 	},	--1
		{ name = 'showings_count', 	type = 'unsigned' 	}	--2
	})
	
	if box.sequence.nouns_ids_autoinc == nil then
		box.schema.sequence.create('nouns_ids_autoinc', {start=1, min=1, cycle=false, step=1 })
	end


	nouns:create_index('primary', 			{ type = 'tree', parts = { 'id' }, sequence = 'nouns_ids_autoinc', if_not_exists = true, unique = true })
	nouns:create_index('word_index', 		{ type = 'hash', parts = { 'noun_word' }, if_not_exists = true, unique = true })
	nouns:create_index('showings_count_index',	{ type = 'tree', parts = { 'showings_count' }, if_not_exists = true, unique = false })
end

--------------------------------Common postcards showings--------------------------------

if box.space.common_postcards_showings == nil then
	local common_postcards_showings = box.schema.space.create('common_postcards_showings', { if_not_exists = true })
	
	common_postcards_showings:format({
		{ name = 'noun_id', 		type = 'unsigned'		},	--0
		{ name = 'postcard_index',	type = 'unsigned'	},  --1
		{ name = 'showings_count', 	type = 'unsigned'	} 	--2
	})
	
	common_postcards_showings:create_index('primary', { type = 'tree', parts = { 'noun_id', 'postcard_index' }, if_not_exists = true, unique = true })
	common_postcards_showings:create_index('noun_showings_count_index', { type = 'tree', parts = { 'noun_id', 'showings_count' }, if_not_exists = true, unique = false })
	common_postcards_showings:create_index('showings_count_index', { type = 'tree', parts = { 'showings_count' }, if_not_exists = true, unique = false })
end

--------------------------------User nouns showings--------------------------------

if box.space.user_nouns_showings == nil then
	local user_nouns_showings = box.schema.space.create('user_nouns_showings', { if_not_exists = true })
	
	user_nouns_showings:format({
		{ name = 'user_id', 		type = 'string'		},	--0
		{ name = 'noun_id',			type = 'unsigned'	},  --1
		{ name = 'showings_count', 	type = 'unsigned'	} 	--2
	})
	
	user_nouns_showings:create_index('primary', { type = 'tree', parts = { 'user_id', 'noun_id' }, if_not_exists = true, unique = true })
	user_nouns_showings:create_index('secondary', { type = 'tree', parts = { 'showings_count' }, if_not_exists = true, unique = false })
	--user_nouns_showings:create_index('user_index', 	{ type = 'tree', parts = { 'user_id' }, if_not_exists = true, unique = false })
	user_nouns_showings:create_index('noun_index', { type = 'tree', parts = { 'noun_id' }, if_not_exists = true, unique = false })
	user_nouns_showings:create_index('user_showings_index', { type = 'tree', parts = { 'user_id', 'showings_count' }, if_not_exists = true, unique = false })
end

--------------------------------User postcards showings--------------------------------

if box.space.user_postcards_showings == nil then
	local user_postcards_showings = box.schema.space.create('user_postcards_showings', { if_not_exists = true })
	
	user_postcards_showings:format({
		{ name = 'user_id', 		type = 'string'		},	--0
		{ name = 'noun_id',			type = 'unsigned'	},  --1
		{ name = 'postcard_index', 	type = 'unsigned'	}	--2
	})
	
	user_postcards_showings:create_index('primary', { type = 'tree', parts = { 'user_id', 'noun_id', 'postcard_index' }, if_not_exists = true, unique = true })
	user_postcards_showings:create_index('postcards_index', { type = 'tree', parts = { 'noun_id', 'postcard_index' }, if_not_exists = true, unique = false })
	--given_nouns:create_index('secondary', { type = 'tree', parts = { 'user_id', 'noun_id' }, unique = false })
end

--------------------------------Common vanilla postcards showings--------------------------------

if box.space.common_vanilla_postcards_showings == nil then
	local common_vanilla_postcards_showings = box.schema.space.create('common_vanilla_postcards_showings', { if_not_exists = true })
	
	common_vanilla_postcards_showings:format({
		{ name = 'postcard_index',	type = 'unsigned'	},  --0
		{ name = 'showings_count', 	type = 'unsigned'	} 	--1
	})
	
	common_vanilla_postcards_showings:create_index('primary', { type = 'tree', parts = { 'postcard_index' }, if_not_exists = true, unique = true })
	common_vanilla_postcards_showings:create_index('showings_count_index', { type = 'tree', parts = { 'showings_count' }, if_not_exists = true, unique = false })
end

--------------------------------User vanilla postcards showings--------------------------------

if box.space.user_vanilla_postcards_showings == nil then
	local user_vanilla_postcards_showings = box.schema.space.create('user_vanilla_postcards_showings', { if_not_exists = true })
	
	user_vanilla_postcards_showings:format({
		{ name = 'user_id', 		type = 'string'		},	--0
		{ name = 'postcard_index', 	type = 'unsigned'	}	--1
	})
	
	user_vanilla_postcards_showings:create_index('primary', { type = 'tree', parts = { 'user_id', 'postcard_index' }, if_not_exists = true, unique = true })
	user_vanilla_postcards_showings:create_index('postcard_index', { type = 'tree', parts = { 'postcard_index' }, if_not_exists = true, unique = false })
end

end

math.randomseed(os.time())

--Init current work nouns
function start_init(nouns_list, postcards_count, vanilla_postcards_count)
	result = {}
	--Select or insert init nouns -> write to result list
	for _, noun in pairs(nouns_list) do
		noun_rows = box.space.nouns.index.word_index:select{noun}
		if #noun_rows == 1 then
			result[noun] = noun_rows[1][1]
		else
			result[noun] = box.space.nouns:insert{box.NULL, noun, 0}[1]
		end
	end
	
	WORK_NOUNS = result --[word] = id
	POSTCARDS_COUNT = postcards_count
	vanilla_POSTCARDS_COUNT = vanilla_postcards_count
	
	return result
end

function random_choose(array)
	return array[math.random(#array)]
end

--Generate start, returns priority regen id or -1
function get_generate_priority()
	local priority_showings_count, prority_list, showings_count, priority_noun_id, priority_postcard_index
	
	priority_showings_count = -1
	prority_list = {}
	for _, noun_row in box.space.nouns.index.showings_count_index:pairs( {}, { iterator = 'REQ'} ) do
		if WORK_NOUNS[noun_row[2]] ~= nil then
			showings_count = noun_row[3]
			if priority_showings_count == -1 then
				priority_showings_count = showings_count
				if showings_count == 0 then
					return -1
				end
			elseif showings_count ~= priority_showings_count then
				break
			end
			
			table.insert(prority_list, noun_row[1])
		end
	end
	
	priority_noun_id = random_choose(prority_list)
	
	prority_list = {}
	priority_showings_count = -1
	for _, postcard_row in box.space.common_postcards_showings:pairs( {priority_noun_id}, { iterator = 'REQ' } ) do
		showings_count = postcard_row[3]
		if priority_showings_count == -1 then
			priority_showings_count = showings_count
		elseif showings_count ~= priority_showings_count then
			break
		end
		
		table.insert(prority_list, postcard_row[2])
	end
	
	if #prority_list ~= 0 then
		priority_postcard_index = random_choose(prority_list)
	else
		return -1
	end
	
	return priority_noun_id, priority_postcard_index
end

--Generate end
function noun_showings_dec(noun_id)
	local noun_row, user_noun_showings
	noun_row = box.space.nouns:select( {noun_id} ) [1]
	if noun_row ~= nil then
		if noun_row[3] > 0 then
			box.space.nouns:update( {noun_id}, { { '-', 3, 1 } } )
		end
	end
	
	for _, user_noun_showings in  box.space.user_nouns_showings.index.noun_index:pairs( {noun_id} ) do
		if user_noun_showings ~= nil then
			if user_noun_showings[3] <= 1 then
				box.space.user_nouns_showings:delete( {user_noun_showings[1], noun_id} )
			else
				box.space.user_nouns_showings:update( {user_noun_showings[1], noun_id}, { { '-', 3, 1 } } )
			end
		end
	end
end

function postcard_showings_dec(noun_id, postcard_index)
	local user_posrcard_showing, common_postcard_showings
	noun_showings_dec(noun_id)
	
	for _, user_posrcard_showing in  box.space.user_postcards_showings.index.postcards_index:pairs( {noun_id, postcard_index} ) do
		if user_posrcard_showing ~= nil then
			box.space.user_postcards_showings:delete( { user_posrcard_showing[1], noun_id, postcard_index } )
		end
	end
	
	common_postcard_showings = box.space.common_postcards_showings:select( {noun_id, postcard_index} ) [1]
	if common_postcard_showings ~= nil then
		
		--if common_postcard_showings[3] <= 1 then
			box.space.common_postcards_showings:delete( { common_postcard_showings[1], common_postcard_showings[2] } )
		--else
		--	box.space.common_postcards_showings:update( { common_postcard_showings[1], common_postcard_showings[2] }, { {'=', 3, common_postcard_showings[3] - 1} } )
		--end
	end
end

--Show postcard
function add_postcard_showing(user_id, noun_id, postcard_index)
	local user_noun_showings, common_noun_showings, new_showings_count
	
	user_noun_showings = box.space.user_nouns_showings:select( {user_id, noun_id} )[1]
	
	if user_noun_showings == nil then
		user_noun_showings = box.space.user_nouns_showings:insert( {user_id, noun_id, 1} )
		new_showings_count = 1
	elseif user_noun_showings[3] < POSTCARDS_COUNT then
		new_showings_count = user_noun_showings[3] + 1
		box.space.user_nouns_showings:update( { user_id, noun_id }, { {'=', 3, new_showings_count} } )
	end
	
	common_noun_showings = box.space.nouns:select( {noun_id} )[1]
	if common_noun_showings[3] < new_showings_count then
		box.space.nouns:update( {noun_id}, { {'=', 3, new_showings_count} } )
	end
	
	if #box.space.user_postcards_showings:select( {user_id, noun_id, postcard_index} ) == 0 then
		box.space.user_postcards_showings:insert( {user_id, noun_id, postcard_index} )
		box.space.common_postcards_showings:upsert( {noun_id, postcard_index, 1}, { {'+', 3, 1} } )
	end
	
	
	
end

function get_next_random_noun_postcard(user_id, noun_id)
	local showed_indices_list, available_indices_list, index, selected_postcard_index
	
	showed_indices_list = {}
	for _, tuple in box.space.user_postcards_showings.index.primary:pairs( {user_id, noun_id} ) do
		showed_indices_list[tuple[3]] = true
	end
	
	available_indices_list = {}
	for index = 0, POSTCARDS_COUNT - 1 do
		if showed_indices_list[index] == nil then
			table.insert(available_indices_list, index)
		end
	end
	
	if #available_indices_list ~= 0 then
		selected_postcard_index = random_choose(available_indices_list)
	else
		selected_postcard_index = math.random(0, POSTCARDS_COUNT - 1)
	end
	
	add_postcard_showing(user_id, noun_id, selected_postcard_index)
	return selected_postcard_index
	
end

function get_next_random_postcard(user_id)
	local postcard_index, min_showings_list, unshowed_nouns, unshowed_nouns_array, noun_showings, min_showings, selected_noun_id, selected_postcard_index
	
	unshowed_nouns = {}
	for _, id in pairs(WORK_NOUNS) do
		unshowed_nouns[id] = true
	end
	
	min_showings_list = {}
	min_showings = -1
	for _, row in box.space.user_nouns_showings.index.user_showings_index:pairs( {user_id}, {iterator = box.index.EQ} ) do
		noun_showings = row[3]
		if min_showings == -1 or noun_showings <= min_showings then
			if min_showings == -1 then
				min_showings = noun_showings
			end
			table.insert(min_showings_list, row[2])
		end
		
		if noun_showings ~= 0 then
			unshowed_nouns[row[2]] = nil
		end
	end
	
	unshowed_nouns_array = {}
	for key, value in pairs(unshowed_nouns) do
		if value ~= nil then
			table.insert(unshowed_nouns_array, key)
		end
	end
	
	
	if #unshowed_nouns_array ~= 0 then
		selected_noun_id = random_choose(unshowed_nouns_array)
	else
		selected_noun_id = random_choose(min_showings_list)
	end
	
	selected_postcard_index = get_next_random_noun_postcard(user_id, selected_noun_id)
	
	return selected_noun_id, selected_postcard_index
end





--Generate start, returns priority regen id or -1
function get_vanilla_generate_priority()
	local priority_showings_count, prority_list, showings_count, priority_postcard_index, postcard_row
	
	priority_showings_count = -1
	prority_list = {}
	for _, postcard_row in box.space.common_vanilla_postcards_showings.index.showings_count_index:pairs( {}, { iterator = 'REQ'} ) do
		showings_count = postcard_row[2]
		if priority_showings_count == -1 then
			priority_showings_count = showings_count
			if showings_count == 0 then
				return -1
			end
		elseif showings_count ~= priority_showings_count then
			break
		end
		
		table.insert(prority_list, postcard_row[1])
	end
	
	if #prority_list ~= 0 then
		return random_choose(prority_list)
	else
		return -1
	end
end

function vanilla_postcard_showings_dec(postcard_index)
	local ommon_vanilla_postcard_showings_row, vanilla_posrcards_showing_row
	
	for _, vanilla_posrcards_showing_row in  box.space.user_vanilla_postcards_showings.index.postcard_index:pairs( {postcard_index} ) do
		box.space.user_vanilla_postcards_showings:delete( { vanilla_posrcards_showing_row[1], postcard_index } )
	end
	
	common_vanilla_postcard_showings_row = box.space.common_vanilla_postcards_showings:select( {postcard_index} ) [1]
	if common_vanilla_postcard_showings_row ~= nil then
		--if common_postcard_showings[3] <= 1 then
			box.space.common_vanilla_postcards_showings:delete( { common_vanilla_postcard_showings_row[1] } )
		--else
		--	box.space.common_postcards_showings:update( { common_vanilla_postcard_showings_row[1], common_vanilla_postcard_showings_row[2] }, { {'=', 3, common_vanilla_postcard_showings_row[3] - 1} } )
		--end
	end
end

--Show vanilla postcard
function add_vanilla_postcard_showing(user_id, postcard_index)
	local user_noun_showings, common_noun_showings, new_showings_count

	if #box.space.user_vanilla_postcards_showings:select( {user_id, postcard_index} ) == 0 then
		box.space.user_vanilla_postcards_showings:insert( {user_id, postcard_index} )
		box.space.common_vanilla_postcards_showings:upsert( {postcard_index, 1}, { {'+', 2, 1} } )
	end
	
end

function get_next_random_vanilla_postcard(user_id)
	local showed_indices_list, available_indices_list, index, selected_postcard_index
	
	showed_indices_list = {}
	for _, tuple in box.space.user_vanilla_postcards_showings.index.primary:pairs( {user_id} ) do
		showed_indices_list[tuple[2]] = true
	end
	
	available_indices_list = {}
	for index = 0, vanilla_POSTCARDS_COUNT - 1 do
		if showed_indices_list[index] == nil then
			table.insert(available_indices_list, index)
		end
	end
	
	if #available_indices_list ~= 0 then
		selected_postcard_index = random_choose(available_indices_list)
	else
		selected_postcard_index = math.random(0, vanilla_POSTCARDS_COUNT - 1)
	end
	
	add_vanilla_postcard_showing(user_id, selected_postcard_index)
	return selected_postcard_index
	
end

function reinit()
	reinitArray = { 
		box.space.nouns,
		box.sequence.nouns_ids_autoinc,
		box.space.common_postcards_showings,
		box.space.user_nouns_showings, 
		box.space.user_postcards_showings,
		box.space.user_vanilla_postcards_showings,
		box.space.common_vanilla_postcards_showings
	}
	for key, value in pairs(reinitArray) do
		if value ~= nil then
			value:drop()
		end
	end
	
	
	init()
end

--reinit()

box.once("data", init)