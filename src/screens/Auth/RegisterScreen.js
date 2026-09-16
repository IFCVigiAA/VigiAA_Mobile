import { LinearGradient } from 'expo-linear-gradient';
import { useState } from 'react';
import { Alert, Image, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from 'react-native';

// O mesmo endereço do seu config.py / ngrok
const API_URL = "https://froglike-cataleya-quirkily.ngrok-free.dev";

export default function RegisterScreen({ navigation }) {
  const [nome, setNome] = useState('');
  const [sobrenome, setSobrenome] = useState('');
  const [usuario, setUsuario] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmaSenha, setConfirmaSenha] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!nome || !sobrenome || !usuario || !email || !senha || !confirmaSenha) {
      Alert.alert("Aviso", "Preencha todos os campos!");
      return;
    }

    if (senha !== confirmaSenha) {
      Alert.alert("Aviso", "As senhas não coincidem!");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          first_name: nome,
          last_name: sobrenome,
          username: usuario,
          email: email,
          password: senha,
          password2: confirmaSenha
        })
      });

      if (response.ok) {
        Alert.alert("Sucesso", "Conta criada com sucesso! Faça login.");
        navigation.goBack(); // Retorna para a tela de Login
      } else {
        const errorData = await response.json();
        let errorMsg = "Erro ao cadastrar. Verifique os dados.";
        
        // Pega a primeira mensagem de erro retornada pelo Django Rest Framework
        const keys = Object.keys(errorData);
        if (keys.length > 0) {
          const firstKey = keys[0];
          errorMsg = `${firstKey}: ${errorData[firstKey][0]}`;
        }
        Alert.alert("Erro", errorMsg);
      }
    } catch (error) {
      Alert.alert("Erro", "Erro de conexão com o servidor.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* Topo com o mesmo Degradê do VigiAA */}
      <LinearGradient
        colors={['#3AC0ED', '#72FC90']}
        style={styles.headerGradient}
      >
        <Image 
          source={require('../../../assets/images/react-logo.png')} // Ajuste o caminho se necessário
          style={styles.logo} 
        />
        <Text style={styles.title}>VigiAA</Text>
        <Text style={styles.subtitle}>Crie sua conta</Text>
      </LinearGradient>

      {/* Formulário com Scroll para não esconder atrás do teclado */}
      <ScrollView contentContainerStyle={styles.formContainer}>
        <TextInput
          style={styles.input}
          placeholder="Nome"
          value={nome}
          onChangeText={setNome}
        />
        <TextInput
          style={styles.input}
          placeholder="Sobrenome"
          value={sobrenome}
          onChangeText={setSobrenome}
        />
        <TextInput
          style={styles.input}
          placeholder="Usuário"
          value={usuario}
          onChangeText={setUsuario}
          autoCapitalize="none"
        />
        <TextInput
          style={styles.input}
          placeholder="Email"
          value={email}
          onChangeText={setEmail}
          keyboardType="email-address"
          autoCapitalize="none"
        />
        <TextInput
          style={styles.input}
          placeholder="Senha"
          value={senha}
          onChangeText={setSenha}
          secureTextEntry
        />
        <TextInput
          style={styles.input}
          placeholder="Confirmar senha"
          value={confirmaSenha}
          onChangeText={setConfirmaSenha}
          secureTextEntry
        />

        <TouchableOpacity style={styles.registerButton} onPress={handleRegister} disabled={loading}>
          <Text style={styles.registerButtonText}>{loading ? "Cadastrando..." : "Cadastrar"}</Text>
        </TouchableOpacity>

        <View style={styles.footerContainer}>
          <Text style={styles.footerText}>Já possui uma conta? </Text>
          <TouchableOpacity onPress={() => navigation.goBack()}>
            <Text style={styles.loginLink}>Faça login</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFF' },
  headerGradient: {
    height: '35%',
    borderBottomLeftRadius: 60,
    borderBottomRightRadius: 60,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: { width: 80, height: 80, marginBottom: 5, resizeMode: 'contain' },
  title: { fontSize: 24, fontWeight: 'bold', color: '#000' },
  subtitle: { fontSize: 15, fontWeight: '600', color: '#000' },
  formContainer: {
    padding: 25,
    paddingBottom: 40,
  },
  input: {
    borderWidth: 1,
    borderColor: '#CCC',
    borderRadius: 12,
    height: 50,
    paddingHorizontal: 15,
    marginBottom: 12,
    backgroundColor: '#FAFAFA',
    color: '#000',
  },
  registerButton: {
    backgroundColor: '#000',
    height: 50,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 10,
    marginBottom: 20,
  },
  registerButtonText: { color: '#FFF', fontWeight: 'bold', fontSize: 16 },
  footerContainer: { flexDirection: 'row', justifyContent: 'center' },
  footerText: { color: '#666' },
  loginLink: { color: '#1D76D2', fontWeight: 'bold' },
});