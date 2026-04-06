import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../services/api_service.dart';
import 'dashboard_page.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final TextEditingController baseUrlController = TextEditingController(
    text: 'https://cadastro-eficiente-1.onrender.com',
  );
  final TextEditingController usuarioController = TextEditingController();
  final TextEditingController senhaController = TextEditingController();

  bool carregando = false;

  @override
  void initState() {
    super.initState();
    _carregarSessao();
  }

  Future<void> _carregarSessao() async {
    final prefs = await SharedPreferences.getInstance();

    baseUrlController.text =
        prefs.getString('base_url') ??
        'https://cadastro-eficiente-1.onrender.com';

    usuarioController.text = prefs.getString('username') ?? '';
  }

  Future<void> _salvarSessao({
    required String baseUrl,
    required String username,
    required String nomeExibicao,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('base_url', baseUrl);
    await prefs.setString('username', username);
    await prefs.setString('nome_exibicao', nomeExibicao);
  }

  Future<void> fazerLogin() async {
    final baseUrl = baseUrlController.text.trim();
    final username = usuarioController.text.trim();
    final password = senhaController.text.trim();

    if (baseUrl.isEmpty || username.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Preencha servidor, usuário e senha.'),
        ),
      );
      return;
    }

    setState(() => carregando = true);

    try {
      final response = await ApiService.login(
        baseUrl: baseUrl,
        username: username,
        password: password,
      );

      if ((response['success'] == true) || (response['ok'] == true)) {
        final nomeExibicao =
            response['nome_exibicao']?.toString() ??
            response['nome']?.toString() ??
            username;

        await _salvarSessao(
          baseUrl: baseUrl,
          username: username,
          nomeExibicao: nomeExibicao,
        );

        if (!mounted) return;

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Login realizado com sucesso')),
        );

        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => DashboardPage(
              username: username,
              nomeExibicao: nomeExibicao,
            ),
          ),
        );
      } else {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              response['message']?.toString() ??
                  response['mensagem']?.toString() ??
                  'Falha no login',
            ),
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro no login: $e')),
      );
    } finally {
      if (mounted) {
        setState(() => carregando = false);
      }
    }
  }

  @override
  void dispose() {
    baseUrlController.dispose();
    usuarioController.dispose();
    senhaController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Cadastro Eficiente'),
        centerTitle: true,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: ListView(
            children: [
              const SizedBox(height: 12),
              TextField(
                controller: baseUrlController,
                decoration: const InputDecoration(
                  labelText: 'Servidor',
                  hintText: 'https://cadastro-eficiente-1.onrender.com',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: usuarioController,
                decoration: const InputDecoration(
                  labelText: 'Usuário',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: senhaController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Senha',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 24),
              SizedBox(
                height: 52,
                child: ElevatedButton(
                  onPressed: carregando ? null : fazerLogin,
                  child: carregando
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Entrar'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}