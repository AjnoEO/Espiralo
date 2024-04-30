import lightbulb

GUILD = int(os.environ['ESPERANTO_GUILD_ID'])
TENOR_KEY = str(os.environ['TENOR_KEY'])
TENOR_CLIENT_KEY = str(os.environ['TENOR_CLIENT_KEY'])
ID = int(os.environ['BOT_ID'])

plugin = lightbulb.Plugin("Steltabulo")

async def ensteltabuligi(self, gilda_id: int, mesagxo: interactions.Message, por: int, kontraux: int, emogxio: interactions.Emoji, emogxio_kontrauxa: interactions.Emoji):
    kanalo = await interactions.get(
        self.client,
        interactions.Channel,
        object_id=db[f"steltabulo_{gilda_id}_kanalo"],
        parent_id=gilda_id,
    )
    mesagxkanalo = await mesagxo.get_channel()
    plusenhavo = await c.plusenhavo_el_mesagxo(self, mesagxo, gilda_id)
    
    steltabula_mesagxo = await kanalo.send(
        content=f"{f'<#{mesagxkanalo.parent_id}> 🢧 ' if (mesagxkanalo.type in range(10, 13)) else ''}<#{mesagxkanalo.id}>\n" \
        f"{emogxio.format}   **x{por}**{f'   |   {emogxio_kontrauxa.format}   **x{kontraux}**' if (emogxio_kontrauxa != None) else ''}\n",
        embeds=plusenhavo,
    )
    
    c.purigi(gilda_id)
    tempo = datetime.utcnow()
    for p in db.prefix(f"steltabulo_{gilda_id}_mesagxoj_{mesagxkanalo.id}.{mesagxo.id}_"):
        del db[p]
    db[f"steltabulo_{gilda_id}_mesagxoj_{mesagxkanalo.id}.{mesagxo.id}_{round(tempo.timestamp())}"] = f"{kanalo.id}.{steltabula_mesagxo.id}"

    await mesagxo.create_reaction(emogxio)

# /STELTABULO AGORDI
@steltabulo.subcommand()
@interactions.option(
	description="En kiun kanalon sendi la sufiĉe stelumitajn afiŝojn"
)
@interactions.option(
	description="Kiom da steloj (aŭ je kiom pli ol kontraŭsteloj) estu por ke la afiŝo ensteltabuliĝu. Defaŭlte: 4"
)
@interactions.option(
	description="Ĉu uzebligi kontraŭstelojn. Defaŭlte: Jes",
	choices=c.jesne,
)
@interactions.option(
	description="Ĉu ignori sinvoĉdonojn. Defaŭlte: Jes",
	choices=c.jesne,
)
@interactions.option(
	description="Ĉu ne ensteltabuligi afiŝon, se la sendinto ĝin kontraŭstelumis. Defaŭlte: Jes",
	choices=c.jesne,
)
async def aktivigi(self, ctx, kanalo: interactions.Channel, kvanto: int = 4, kontrauxsteloj: int = 1, ignori_sinstelumojn: int = 1, stelblokado: int = 1):
	"""Agordi la steltabulon kaj aktivigi ĝin"""
	gilda_id = ctx.guild.id
	sxlosiloj = db.keys()
	if (f"steltabulo_{gilda_id}_kanalo" not in sxlosiloj):
		if (kvanto <= 0):
			await ctx.send("""🚫 `kvanto` devas esti pozitiva nombro.""", ephemeral=True)
			return None
		if (kanalo.type != interactions.ChannelType.GUILD_TEXT):
			await ctx.send("""🚫 `kanalo` devas esti normala tekstkanalo.""", ephemeral=True)
			return None
		try:
			mesagxo = await kanalo.send("**Agordado de la kanalo kiel steltabula...**")
		except:
			await ctx.send(f"""🚫 `kanalo`=<#{kanalo.id}> ne alireblas por mi.""", ephemeral=True)
			return None
		else:
			await mesagxo.delete("Permeskontrola mesaĝo")
		teksto = \
			f"**Agordado...**\n" \
			f"> _Kanalo:_ <#{kanalo.id}>\n" \
			f"> _Minimume da steloj:_ {kvanto if not kontrauxsteloj else f'je {kvanto} pli ol da kontraŭsteloj'}\n" \
			f"> _La emoĝio:_ `Neniu, bonvolu reagumi per la taŭga emoĝio`\n"
		if (not not kontrauxsteloj):
			teksto += f"> _La kontraŭa emoĝio:_ `Neniu, bonvolu reagumi per la taŭga emoĝio`\n"
		teksto += f"\n_Ne reagumu por nuligi la agon_"
		await ctx.send(teksto)
		db[f"steltabulo_{gilda_id}_kanalo"] = str(kanalo.id)
		db[f"steltabulo_{gilda_id}_kvanto"] = str(kvanto)
		db[f"steltabulo_{gilda_id}_is_sb"] = str(ignori_sinstelumojn) + str(stelblokado)
		if (f"steltabulo_{gilda_id}_emogxio" in sxlosiloj): del db[f"steltabulo_{gilda_id}_emogxio"]
		if (f"steltabulo_{gilda_id}_emogxio_kontrauxa" in sxlosiloj): del db[f"steltabulo_{gilda_id}_emogxio_kontrauxa"]
	else:
		await ctx.send("""🚫 Jam estas aktiva steltabulo. Agordu ĝin per `/steltabulo agordi` kaj `/steltabulo emogxioj`""", ephemeral=True)

@steltabulo.subcommand()
@interactions.option(
	description="En kiun kanalon sendi la sufiĉe stelumitajn afiŝojn"
)
@interactions.option(
	description="Kiom da steloj (aŭ je kiom pli ol kontraŭsteloj) estu por ke la afiŝo ensteltabuliĝu"
)
@interactions.option(
	description="Ĉu ignori sinstelumojn (kaj sinkontraŭstelumojn)",
	choices=c.jesne,
)
@interactions.option(
	description="Ĉu ne ensteltabuligi afiŝon, se la sendinto ĝin kontraŭstelumis",
	choices=c.jesne,
)
async def agordi(self, ctx, kanalo: interactions.Channel = None, kvanto: int = None, ignori_sinstelumojn: int = None, stelblokado: int = None):
	"""Reagordi la steltabulon kaj vidi ĝiajn agordojn"""
	gilda_id = ctx.guild.id
	sxlosiloj = db.keys()
	kanala_id = 0
	if (f"steltabulo_{gilda_id}_emogxio" in sxlosiloj):
		if (kvanto != None and kvanto <= 0):
			await ctx.send("""🚫 `kvanto` devas esti pozitiva nombro.""", ephemeral=True)
			return None            
		if (kanalo != None and kanalo.type != interactions.ChannelType.GUILD_TEXT):
			await ctx.send("""🚫 `kanalo` devas esti normala tekstkanalo.""", ephemeral=True)
			return None
		if (kanalo != None):
			try:
				mesagxo = await kanalo.send("**Agordado de la kanalo kiel steltabula...**")
			except:
				await ctx.send(f"""🚫 `kanalo`=<#{kanalo.id}> ne alireblas por mi.""", ephemeral=True)
				return None
			else:
				await mesagxo.delete("Permeskontrola mesaĝo")
				kanala_id = kanalo.id
				db[f"steltabulo_{gilda_id}_kanalo"] = str(kanala_id)
		else:
			kanala_id = db[f"steltabulo_{gilda_id}_kanalo"]
		kv = kvanto
		if (kv == None): kv = db[f"steltabulo_{gilda_id}_kvanto"]
		is_sb = str(ignori_sinstelumojn) if (ignori_sinstelumojn != None) else db[f"steltabulo_{gilda_id}_is_sb"][0]
		is_sb += str(stelblokado) if (stelblokado != None) else db[f"steltabulo_{gilda_id}_is_sb"][1]
		db[f"steltabulo_{gilda_id}_kvanto"] = str(kv)
		db[f"steltabulo_{gilda_id}_is_sb"] = str(is_sb)
		teksto = \
			f"**La steltabulaj agordoj:**\n" \
			f"> _Kanalo:_ <#{kanala_id}>\n" \
			f"> _Minimume da steloj:_ {kv if f'steltabulo_{gilda_id}_emogxio_kontrauxa' not in sxlosiloj else f'je {kv} pli ol da kontraŭsteloj'}\n" \
			f"> _Sinstelumoj {'ne ' if is_sb[0]=='1' else ''}enkalkuliĝas_\n" \
			f"> _Sinkontraŭstelumoj {'ne nepre ' if is_sb[1]=='0' else ''}malpermesas ensteltabuligon_\n"
		await ctx.send(teksto)
	else:
		await ctx.send("""🚫 Ankoraŭ ne estas aktiva steltabulo. Aktivigu ĝin per `/steltabulo aktivigi`""", ephemeral=True)

@steltabulo.subcommand()
async def emogxioj(self, ctx):
	"""Reelekti la emoĝiojn por steltabulo. La jamaj steltabulaj mesaĝoj ne plu sinĥroniĝos!"""
	gilda_id = ctx.guild.id
	sxlosiloj = db.keys()
	if (f"steltabulo_{gilda_id}_emogxio" in sxlosiloj):
		del db[f"steltabulo_{gilda_id}_emogxio"]
		teksto = \
			"**Steltabulaj emoĝioj:**\n" \
			"> _La pora emoĝio:_ `Neniu, bonvolu reagumi per la taŭga emoĝio`\n"
		if (f"steltabulo_{gilda_id}_emogxio_kontrauxa" in sxlosiloj):
			del db[f"steltabulo_{gilda_id}_emogxio_kontrauxa"]
			teksto += "> _La kontraŭa emoĝio:_ `Neniu, bonvolu reagumi per la taŭga emoĝio`\n"
		for e in db.prefix(f"steltabulo_{gilda_id}_mesagxoj_"):
			del db[e]
		await ctx.send(teksto)
	else:
		await ctx.send("""🚫 Ankoraŭ ne estas aktiva steltabulo. Aktivigu ĝin per `/steltabulo aktivigi`""", ephemeral=True)

@steltabulo.subcommand()
async def malaktivigi(self, ctx):
	"""Malaktivigi la steltabulon. La agordoj malaperos! La jamaj steltabulaj mesaĝoj ne plu sinĥroniĝos!"""
	gilda_id = ctx.guild.id
	sxlosiloj = db.keys()
	if (f"steltabulo_{gilda_id}_kanalo" in sxlosiloj): 
		del db[f"steltabulo_{gilda_id}_kanalo"]
		if (f"steltabulo_{gilda_id}_kvanto" in sxlosiloj): del db[f"steltabulo_{gilda_id}_kvanto"]
		if (f"steltabulo_{gilda_id}_is_sb" in sxlosiloj): del db[f"steltabulo_{gilda_id}_is_sb"]
		if (f"steltabulo_{gilda_id}_emogxio" in sxlosiloj): del db[f"steltabulo_{gilda_id}_emogxio"]
		if (f"steltabulo_{gilda_id}_emogxio_kontrauxa" in sxlosiloj): del db[f"steltabulo_{gilda_id}_emogxio_kontrauxa"]
		for e in db.prefix(f"steltabulo_{gilda_id}_mesagxoj_"):
			del db[e]
		await ctx.send("**La steltabulo malaktiviĝis**")
	else:
		await ctx.send("**La steltabulo jam estas malaktiva**")

# PRITRAKTADO DE ALDONOJ DE REAGUMOJ
@interactions.extension_listener()
async def on_message_reaction_add(self, reagumo: interactions.MessageReaction):
	steltabulaj_sxlosiloj = db.prefix("steltabulo_")
	gilda_id = reagumo.guild_id
	mesagxo = await interactions.get(
		self.client,
		interactions.Message,
		object_id=reagumo.message_id,
		parent_id=reagumo.channel_id,
		force="http"
	)
	if (f"steltabulo_{gilda_id}_kanalo" in steltabulaj_sxlosiloj and reagumo.user_id != ID):
		teksto = mesagxo.content
		if ((mesagxo.author.id == ID) and (teksto[:15] == "**Agordado...**" or teksto[:24] == "**Steltabulaj emoĝioj:**") and (mesagxo.interaction.user.id == reagumo.user_id)):
			teksto = re.sub(r"`Neniu, bonvolu reagumi per la taŭga emoĝio`", reagumo.emoji.format, teksto, 1)
			if (f"steltabulo_{str(gilda_id)}_emogxio" not in steltabulaj_sxlosiloj):
				db[f"steltabulo_{str(gilda_id)}_emogxio"] = f"i{str(reagumo.emoji.id)}" if (reagumo.emoji.id != None) else f"n{str(reagumo.emoji.name)}"
				if (re.search(r"_La kontraŭa emoĝio:_", teksto) == None):
					for e in db.prefix(f"steltabulo_{gilda_id}_mesagxoj_"):
						del db[e]
					teksto = re.sub(r"\*+Agordado\.+\*+", "**Sukcese agordite**", teksto)
			elif (re.search(r"_La kontraŭa emoĝio:_", teksto) != None and f"steltabulo_{str(gilda_id)}_emogxio_kontrauxa" not in steltabulaj_sxlosiloj):
				db[f"steltabulo_{str(gilda_id)}_emogxio_kontrauxa"] = f"i{str(reagumo.emoji.id)}" if (reagumo.emoji.id != None) else f"n{str(reagumo.emoji.name)}"
				for e in db.prefix(f"steltabulo_{gilda_id}_mesagxoj_"):
					del db[e]
				teksto = re.sub(r"\*+Agordado\.+\*+", "**Sukcese agordite**", teksto)
			await mesagxo.edit(teksto)

		elif (f"steltabulo_{gilda_id}_emogxio" in steltabulaj_sxlosiloj):
			is_sb = db[f"steltabulo_{gilda_id}_is_sb"]
			e_id = db[f"steltabulo_{gilda_id}_emogxio"]
			emogxio = await c.emogxio_el_datumbazo(self, gilda_id, e_id)
			emogxio_kontrauxa = None
			if (f"steltabulo_{gilda_id}_emogxio_kontrauxa" in steltabulaj_sxlosiloj):
				ek_id = db[f"steltabulo_{gilda_id}_emogxio_kontrauxa"]
				emogxio_kontrauxa = await c.emogxio_el_datumbazo(self, gilda_id, ek_id)
			if (reagumo.emoji.format == emogxio.format or (emogxio_kontrauxa != None and reagumo.emoji.format == emogxio_kontrauxa.format)):
				kvanto_pora = c.reaguma_kvanto(mesagxo, emogxio)
				kvanto_kontrauxa = c.reaguma_kvanto(mesagxo, emogxio_kontrauxa)
				if (is_sb != '00' and emogxio_kontrauxa != None):
					reagumintoj = await mesagxo.get_users_from_reaction(emogxio_kontrauxa)
					identigiloj = [u.id for u in reagumintoj]
					if (mesagxo.author.id in identigiloj):
						kvanto_kontrauxa = (kvanto_pora if (is_sb[1] == '1') else kvanto_kontrauxa-1)
				reagumintoj = await mesagxo.get_users_from_reaction(emogxio)
				identigiloj = [u.id for u in reagumintoj]
				if (is_sb[0] == '1' and mesagxo.author.id in identigiloj):
					kvanto_pora -= 1

				if (kvanto_pora-kvanto_kontrauxa >= int(db[f"steltabulo_{gilda_id}_kvanto"]) and ID not in identigiloj):

					await ensteltabuligi(self, gilda_id, mesagxo, kvanto_pora, kvanto_kontrauxa, emogxio, emogxio_kontrauxa)

				else:
					await c.gxisdatigi(self, gilda_id, reagumo.channel_id, reagumo.message_id)

@interactions.extension_listener()
async def on_message_reaction_remove(self, reagumo: interactions.MessageReaction):

	steltabulaj_sxlosiloj = db.prefix("steltabulo_")
	gilda_id = reagumo.guild_id
	mesagxo = await interactions.get(
		self.client,
		interactions.Message,
		object_id=reagumo.message_id,
		parent_id=reagumo.channel_id,
		force="http"
	)
	if (f"steltabulo_{gilda_id}_emogxio" in steltabulaj_sxlosiloj):
		e_id = db[f"steltabulo_{gilda_id}_emogxio"]
		emogxio = await c.emogxio_el_datumbazo(self, gilda_id, e_id)
		emogxio_kontrauxa = None
		if (f"steltabulo_{gilda_id}_emogxio_kontrauxa" in steltabulaj_sxlosiloj):
			ek_id = db[f"steltabulo_{gilda_id}_emogxio_kontrauxa"]
			emogxio_kontrauxa = await c.emogxio_el_datumbazo(self, gilda_id, ek_id)
		if (reagumo.emoji.format == emogxio.format or (emogxio_kontrauxa != None and reagumo.emoji.format == emogxio_kontrauxa.format)):
			kvanto_pora = c.reaguma_kvanto(mesagxo, emogxio)
			kvanto_kontrauxa = c.reaguma_kvanto(mesagxo, emogxio_kontrauxa)
			reagumintoj = await mesagxo.get_users_from_reaction(emogxio)
			identigiloj = [u.id for u in reagumintoj]

			if (kvanto_pora-kvanto_kontrauxa >= int(db[f"steltabulo_{gilda_id}_kvanto"]) and ID not in identigiloj):

				await ensteltabuligi(self, gilda_id, mesagxo, kvanto_pora, kvanto_kontrauxa, emogxio, emogxio_kontrauxa)

			else:
				await c.gxisdatigi(self, gilda_id, reagumo.channel_id, reagumo.message_id)

